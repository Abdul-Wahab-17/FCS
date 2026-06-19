import { useEffect } from 'react';
import { API_BASE } from '../utils/constants';
import type { Violation } from '../types';

function wsUrl(): string {
  return API_BASE.replace(/^http/, 'ws') + '/ws/alerts';
}

export function useWebSocket(onAlert: (alert: Violation) => void) {
  useEffect(() => {
    const socket = new WebSocket(wsUrl());

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === 'COMPLIANCE_ALERT') {
        onAlert({
          event_id: payload.event_id,
          timestamp: payload.timestamp,
          clip_id: '',
          zone: payload.zone,
          behavior_class: payload.behavior_class,
          policy_rule_ref: '',
          event_description: payload.description,
          severity: payload.severity,
          escalation_action: 'Database log + real-time dashboard alert',
          confidence: 0,
          frame_number: 0
        });
      }
    };

    return () => socket.close();
  }, [onAlert]);
}
