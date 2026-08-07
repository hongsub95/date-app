type UnauthorizedHandler = () => void;

let handler: UnauthorizedHandler | null = null;

export function setUnauthorizedHandler(nextHandler: UnauthorizedHandler | null) {
  handler = nextHandler;
}

export function notifyUnauthorized() {
  handler?.();
}
