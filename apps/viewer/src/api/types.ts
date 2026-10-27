export type { ContractTypes } from './generated/types';
import type { ContractTypes } from './generated/types';
export type DtoName = keyof ContractTypes;
export type Dto<K extends DtoName> = ContractTypes[K];
