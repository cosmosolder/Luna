# Weather API Tool using FastMCP
# This script provides a FastMCP server that allows users to get weather alerts
# and forecasts using the National Weather Service (NWS) API.
import sys
from typing import Any
import httpx
from anthropic import Anthropic
from mcp.server.fastmcp import FastMCP
import pandas as pd


# Initialize FastMCP server
mcp = FastMCP("luna", description="Luna PE API Tool using FastMCP", version="1.0.0")

# Constants
XLSX_FILE = "/Users/johnsolder/Library/CloudStorage/OneDrive-Coherent/Excel Examples/Mortgage Model/MTG_AMORT_CALC/mortgage-amort-calculator.xlsx"


def convert_xls_to_df(xlsx_file: str) -> pd.DataFrame:
    """Convert an XLSX file to a Pandas DataFrame."""
    try:
        #df = pd.read_excel(xlsx_file, engine='openpyxl')
        dfs = pd.read_excel(xlsx_file, sheet_name=None,engine='openpyxl')
        combined_df = pd.concat(dfs.values(), ignore_index=True)
        return combined_df
    except Exception as e:
        print(f"Error reading XLSX file: {e}", file=sys.stderr)
        return pd.DataFrame()  # Return empty DataFrame on error  

def convert_df_to_md_table(df: pd.DataFrame) -> str:
    """Convert a Pandas DataFrame to a Markdown table."""
    if df.empty:
        return "No data available."

    # Replace newlines with <br> for HTML-like line breaks within Markdown
    df = df.apply(lambda x: x.str.replace('\n', '<br>') if x.dtype == 'object' else x)

    md_table = df.to_markdown(index=False)

    #print(md_table)

    return md_table   

def build_mcp_input(markdown_table: str) -> str:
    #Construct Your "Model Context Protocol" Input:
    #This is where you combine the Markdown table with any other elements required by your "MCP" (e.g., specific instructions, preamble text, custom tags).

    LoanAmt = 500000.00
    IntRate = 7.0
    LoanTerm = 30

    mcp_input = f"""
    Loan Amount: {LoanAmt}
    Interest Rate: {IntRate}
    Loan Term: {LoanTerm} years

    Please analyze the following financial summary data for the specified period.
    Identify key trends, growth rates, and any significant changes.

    {markdown_table}

    Provide a concise executive summary of the financial performance.
    """
    print(mcp_input)
    return ""


@mcp.tool()
async def get_workbook(workbook: str) -> str:
    """Get the contents of a workbook.

    Args:
        workbook: Name of the workbook to retrieve
    """
    #if workbook != XLSX_FILE:
    #    return f"Workbook '{workbook}' not found."

    print('In get_workbook',workbook)

    df = convert_xls_to_df(workbook)
    if df.empty:
        return "No data available in the workbook."

    markdown_table = convert_df_to_md_table(df)
    build_mcp_input(markdown_table)
    return markdown_table   

    #print('IN LUNA.PY +++++++++++++++++++++++', file=sys.stderr)
    #print('Sheet',XLSX_FILE, file=sys.stderr)
    #convert_xls_to_df(XLSX_FILE)
    #new_md_table = convert_df_to_md_table(convert_xls_to_df(workbook))



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
