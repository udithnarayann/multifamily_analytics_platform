interface ErrorStateProps {
  message: string;
}

export function ErrorState({ message }: ErrorStateProps) {
  return (
    <div className="state-card error">
      <strong>Unable to load dashboard data.</strong>
      <p>{message}</p>
    </div>
  );
}
