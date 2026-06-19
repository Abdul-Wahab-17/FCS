interface ExportButtonProps {
  href: string;
  label: string;
}

export default function ExportButton({ href, label }: ExportButtonProps) {
  return (
    <a className="button secondary export-link" href={href}>
      {label}
    </a>
  );
}
