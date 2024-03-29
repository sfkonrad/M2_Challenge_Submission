# -*- coding: utf-8 -*-
"""Loan Qualifier Application.

This is a command line application to match applicants with qualifying loans.

Example:
    $ python app.py
"""
import sys
from pathlib import Path
import fire
import questionary

from qualifier.utils.fileio import load_csv, save_csv

from qualifier.utils.calculators import (
    calculate_monthly_debt_ratio,
    calculate_loan_to_value_ratio,
)

from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value


def load_bank_data():
    """Ask for the file path to the latest banking data and load the CSV file.

    Returns:
        The bank data from the data rate sheet CSV file.
    """

    csvpath = questionary.text("Enter a file path to a rate-sheet (.csv):").ask()
    csvpath = Path(csvpath)
    if not csvpath.exists():
        sys.exit(f"Oops! Can't find this path: {csvpath}")

    return load_csv(csvpath)


def get_applicant_info():
    """Request the applicant's Income, Debt, and Loan information.
    
    Args:
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns: Information necessary for processing the loan application.

    """
    credit_score = questionary.text("Please provide your credit score:").ask()
    debt = questionary.text("Please provide your current amount of monthly debt:").ask()
    income = questionary.text("Please provide your total monthly income:").ask()
    loan_amount = questionary.text("Please provide your desired loan amount:").ask()
    home_value = questionary.text("Please provide your home's value:").ask()

    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    # print(credit_score, debt, income, loan_amount, home_value)

    return credit_score, debt, income, loan_amount, home_value


def find_qualifying_loans(bank_data, credit_score, debt, income, loan, home_value):
    """Determine which loans the user qualifies for.

    Loan qualification criteria is based on:
        - Credit Score
        - Loan Size
        - Debit to Income ratio (calculated)
        - Loan to Value ratio (calculated)

    Args:
        bank_data (list): A list of bank data.
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns:
        A list of the banks willing to underwrite the loan.

    """

    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt, income)
    print(f"The monthly debt to income ratio is {monthly_debt_ratio:.02f}")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan, home_value)
    print(f"The loan to value ratio is {loan_to_value_ratio:.02f}.")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan, bank_data)
    bank_data_filtered = filter_credit_score(credit_score, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(loan_to_value_ratio, bank_data_filtered)
    
    print(f"Found {len(bank_data_filtered)} qualifying loans")

    print(bank_data_filtered)

    return bank_data_filtered


def save_qualifying_loans(qualifying_loans):
    """Request a file path for saving the qualifying loans to a CSV file.

    Args:
        qualifying_loans (list of lists): The qualifying bank loans.
    """
    if (len(qualifying_loans)) < 1:
        sys.exit("There are no qualifying loans. Exiting the Qualifier App.")
        
    save_prompt = questionary.confirm("Would you like to save the list of Qualifying Loans?").ask()

    if save_prompt:
        csvpath = questionary.text(
            "Enter a file path for saving the qualifying_loans.csv:"
        ).ask()
        save_csv(csvpath, qualifying_loans)
        print(">>>> Great!!! The Qualifying Loans have been saved to the path provided. <<<<")

    




def run():
    """The main function for running the script."""

    # Load the latest Bank data
    bank_data = load_bank_data()

    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )

    # Save qualifying loans
    save_qualifying_loans(qualifying_loans)


if __name__ == "__main__":
    fire.Fire(run)

# i/o Examples:
# in... 
# C:/Users/konra/DesKtop/FinTech_Workspace/M02/M2_Challenge/W-A-R-N-I-N-G-_-L-I-V-E-_-G-I-T-_-R-E-P-O-M02/Module 2 Challenge - Loan Qualifier Software Design/loan_qualifier/data/daily_rate_sheet.csv
# out...
# C:/Users/konra/DesKtop/FinTech_Workspace/M02/M2_Challenge/W-A-R-N-I-N-G-_-L-I-V-E-_-G-I-T-_-R-E-P-O-M02/Module 2 Challenge - Loan Qualifier Software Design/loan_qualifier/qualifying_loans.csv