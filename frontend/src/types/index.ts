export interface AccountSummary {
    totalBalance: number;
    availableBalance: number;
    todayPnL: number;
    totalPnL: number;
}

export interface Position {
    symbol: string;
    amount: number;
    avgPrice: number;
    currentPrice: number;
    pnl: number;
}

export type BotStatus = 'idle' | 'running' | 'stopped' | 'error';
// Optional: helper constant if needed for values, but usually raw strings are fine in this mode
export const BOT_STATUS = {
    IDLE: 'idle',
    RUNNING: 'running',
    STOPPED: 'stopped',
    ERROR: 'error'
} as const;
