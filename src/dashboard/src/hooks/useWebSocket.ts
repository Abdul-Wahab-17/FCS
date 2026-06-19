import { useEffect, useRef } from 'react';
import { API_BASE } from '../utils/constants';
import type { Violation } from '../types';

function wsUrl(): string {
  return API_BASE.replace(/^http/, 'ws') + '/ws/alerts';
}

export function useWebSocket(onAlert: (alert: Violation) => void) {
  const reconnectDelay = 3000;
  const initialDelay = 800;

  const socketRef = useRef<WebSocket | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const connectedOnceRef = useRef(false);

  useEffect(() => {
    let isUnmounted = false;

    const connect = () => {
      if (isUnmounted) return;

      const socket = new WebSocket(wsUrl());
      socketRef.current = socket;

      socket.onopen = () => {
        connectedOnceRef.current = true;
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);

          if (payload.type !== 'COMPLIANCE_ALERT') return;

          onAlert({
            event_id: payload.event_id,
            timestamp: payload.timestamp,
            clip_id: payload.clip_id ?? '',
            zone: payload.zone,
            behavior_class: payload.behavior_class,
            policy_rule_ref: payload.policy_rule_ref ?? '',
            event_description: payload.description,
            severity: payload.severity,
            escalation_action: payload.escalation_action ?? '',
            confidence: payload.confidence ?? 0,
            frame_number: payload.frame_number ?? 0,
          });
        } catch (e) {
          console.error('WebSocket message parse error', e);
        }
      };

      socket.onclose = () => {
        if (!isUnmounted) {
          timeoutRef.current = setTimeout(connect, reconnectDelay);
        }
      };

      socket.onerror = () => {
        if (connectedOnceRef.current) {
          console.warn('WebSocket connection lost; reconnecting…');
        }
      };
    };

    timeoutRef.current = setTimeout(connect, initialDelay);

    return () => {
      isUnmounted = true;

      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [onAlert]);
}
