#!/usr/bin/env python3
"""
Calculate the full financial impact of mortgage rate difference
Including impact on capital vs interest payments
"""

def calculate_mortgage_impact(principal, rate1, rate2, years=25, fixed_years=5):
    """Calculate full mortgage impact of rate difference"""
    
    # Convert annual rates to monthly
    monthly_rate1 = rate1 / 100 / 12
    monthly_rate2 = rate2 / 100 / 12
    
    # Total number of payments
    total_payments = years * 12
    
    # Calculate monthly payments
    payment1 = principal * (monthly_rate1 * (1 + monthly_rate1)**total_payments) / ((1 + monthly_rate1)**total_payments - 1)
    payment2 = principal * (monthly_rate2 * (1 + monthly_rate2)**total_payments) / ((1 + monthly_rate2)**total_payments - 1)
    
    print(f"Mortgage amount: £{principal:,.2f}")
    print(f"Term: {years} years")
    print(f"\n--- MONTHLY PAYMENTS ---")
    print(f"At {rate1}%: £{payment1:,.2f}")
    print(f"At {rate2}%: £{payment2:,.2f}")
    print(f"Extra per month: £{payment2 - payment1:,.2f}")
    
    # Calculate capital paid off in first 5 years
    balance1 = principal
    balance2 = principal
    total_interest1 = 0
    total_interest2 = 0
    
    for month in range(fixed_years * 12):
        # Interest portions
        interest1 = balance1 * monthly_rate1
        interest2 = balance2 * monthly_rate2
        
        # Capital portions
        capital1 = payment1 - interest1
        capital2 = payment2 - interest2
        
        # Update balances
        balance1 -= capital1
        balance2 -= capital2
        
        # Track total interest
        total_interest1 += interest1
        total_interest2 += interest2
    
    capital_paid1 = principal - balance1
    capital_paid2 = principal - balance2
    
    print(f"\n--- AFTER {fixed_years} YEARS (FIXED TERM) ---")
    print(f"\nAt {rate1}%:")
    print(f"  Total paid: £{payment1 * fixed_years * 12:,.2f}")
    print(f"  Interest paid: £{total_interest1:,.2f}")
    print(f"  Capital paid off: £{capital_paid1:,.2f}")
    print(f"  Remaining balance: £{balance1:,.2f}")
    
    print(f"\nAt {rate2}%:")
    print(f"  Total paid: £{payment2 * fixed_years * 12:,.2f}")
    print(f"  Interest paid: £{total_interest2:,.2f}")
    print(f"  Capital paid off: £{capital_paid2:,.2f}")
    print(f"  Remaining balance: £{balance2:,.2f}")
    
    print(f"\n--- IMPACT OF HIGHER RATE ---")
    print(f"Extra interest paid: £{total_interest2 - total_interest1:,.2f}")
    print(f"Less capital paid off: £{capital_paid1 - capital_paid2:,.2f}")
    print(f"Higher balance remaining: £{balance2 - balance1:,.2f}")
    
    # Calculate total cost over full mortgage term
    total_cost1 = payment1 * total_payments
    total_cost2 = payment2 * total_payments
    
    print(f"\n--- FULL MORTGAGE TERM ({years} YEARS) ---")
    print(f"Total cost at {rate1}%: £{total_cost1:,.2f}")
    print(f"Total cost at {rate2}%: £{total_cost2:,.2f}")
    print(f"TOTAL EXTRA COST: £{total_cost2 - total_cost1:,.2f}")
    
    return {
        'extra_monthly': payment2 - payment1,
        'extra_interest_5yr': total_interest2 - total_interest1,
        'less_capital_5yr': capital_paid1 - capital_paid2,
        'total_extra_cost': total_cost2 - total_cost1
    }

# Calculate impact
print("MORTGAGE IMPACT ANALYSIS - CREST NICHOLSON DELAYS")
print("=" * 50)
impact = calculate_mortgage_impact(
    principal=490000,
    rate1=4.38,  # Best rate available
    rate2=4.72,  # Rate they got
    years=25,     # Typical mortgage term
    fixed_years=5 # Fixed period
)