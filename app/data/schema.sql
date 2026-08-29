-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    email TEXT NOT NULL,
    customer_since DATE NOT NULL,
    country TEXT NOT NULL,
    status TEXT NOT NULL
);

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    account_number TEXT NOT NULL,
    account_type TEXT NOT NULL,
    currency TEXT NOT NULL,
    opening_balance DECIMAL(20, 2) NOT NULL,
    current_balance DECIMAL(20, 2) NOT NULL,
    opened_at DATE NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    from_account_id TEXT NOT NULL,
    to_account_id TEXT NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    currency TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    transaction_date DATETIME NOT NULL,
    status TEXT NOT NULL,
    reference TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    completed_at DATETIME,
    FOREIGN KEY (from_account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (to_account_id) REFERENCES accounts(account_id)
);

-- Ledger entries table
CREATE TABLE IF NOT EXISTS ledger_entries (
    ledger_entry_id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    entry_type TEXT NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    currency TEXT NOT NULL,
    balance_before DECIMAL(20, 2) NOT NULL,
    balance_after DECIMAL(20, 2) NOT NULL,
    created_at DATETIME NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- Investigation cases table
CREATE TABLE IF NOT EXISTS investigation_cases (
    case_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    complaint TEXT NOT NULL,
    submitted_at DATETIME NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- Case transactions table
CREATE TABLE IF NOT EXISTS case_transactions (
    case_id TEXT NOT NULL,
    transaction_id TEXT NOT NULL,
    relevance TEXT NOT NULL,
    PRIMARY KEY (case_id, transaction_id),
    FOREIGN KEY (case_id) REFERENCES investigation_cases(case_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_accounts_customer_id ON accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_from_account ON transactions(from_account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_to_account ON transactions(to_account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_ledger_entries_transaction ON ledger_entries(transaction_id);
CREATE INDEX IF NOT EXISTS idx_ledger_entries_account ON ledger_entries(account_id);
CREATE INDEX IF NOT EXISTS idx_investigation_cases_customer ON investigation_cases(customer_id);
CREATE INDEX IF NOT EXISTS idx_investigation_cases_account ON investigation_cases(account_id);
CREATE INDEX IF NOT EXISTS idx_investigation_cases_status ON investigation_cases(status);
