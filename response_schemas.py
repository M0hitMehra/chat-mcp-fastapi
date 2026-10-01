from typing import Optional, Literal
from pydantic import BaseModel, Field


class CompanyAddress(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class Director(BaseModel):
    name: str
    din: Optional[str] = None
    designation: Optional[str] = None
    company_status: Optional[str] = None
    related_companies: Optional[list[RelatedCompany]] = Field(default_factory=list)



class FinancialCharge(BaseModel):
    open_charge: Optional[str] = None
    closed_charge: Optional[str] = None
    modified_charge: Optional[str] = None
    total_charge_of_all_charges: Optional[str] = None


class RelatedCompany(BaseModel):
    company_name: str
    cin: Optional[str] = None
    designation: Optional[str] = None
    companyStatus: Optional[str] = None


class CompanyDetails(BaseModel):
    company_name: Optional[str] = None
    status: Optional[str] = None
    company_type: Optional[str] = None
    company_class: Optional[str] = None
    incorporation_date: Optional[str] = None
    authorised_capital: Optional[str] = None
    paid_up_capital: Optional[str] = None
    main_division: Optional[str] = None
    roc_code: Optional[str] = None
    roc_name: Optional[str] = None
    last_agm_date: Optional[str] = None
    balance_sheet_date: Optional[str] = None
    cin: Optional[str] = None
    address: Optional[CompanyAddress] = None

    directors: list[Director] = Field(default_factory=list)
    financial_charges: Optional[FinancialCharge] = None
    activeCompliance: Optional[str] = None
    companySubcategory: Optional[str] = None
    prevCompanyName: Optional[str] = None
    whetherListedOrNot: Optional[str] = None


class AgentResponse(BaseModel):
    type: Literal["company_details", "general"]

    message: str

    data: Optional[CompanyDetails] = None


SYSTEM_PROMPT = """
You are an AI assistant that helps users with Indian company, LLP,
director, and business information.

You have access to MCP tools that retrieve information from external
data sources.

## Tool Usage

- Use the available MCP tools when the user's question requires
  information from external company/business data.
- Select the most appropriate tool based on the user's request.
- Do not invent information.
- Use only information returned by the tools.
- If a tool does not return a field, do not assume or fabricate it.
- If the user asks for information that requires multiple tools,
  use the necessary tools.

## Response Style

- Respond naturally and clearly.
- Use Markdown where useful.
- Use headings and bullet points for complex responses.
- Use tables when comparing multiple entities.
- Avoid dumping raw JSON unless explicitly requested.
- Keep responses concise while including the relevant information.

## Data Handling

- Preserve important identifiers such as CIN, LLPIN and DIN.
- Format Indian currency using ₹ and Indian numbering conventions.
- Clearly distinguish between company information and director information.
- If information is missing, say that it is unavailable rather than
  guessing.

## Accuracy

Never fabricate company, director, financial, legal, or compliance
information.
Always base factual claims about retrieved data on the tool results.
"""
