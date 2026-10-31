/* Generated contract. */

export type Code = string;
export type Message = string;

export interface ErrorEnvelope {
  error: Error;
}
export interface Error {
  code: Code;
  message: Message;
}
