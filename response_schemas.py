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
    related_companies: Optional[list[RelatedCompany]] = Field(default_factory=list)
    activeCompliance: Optional[str] = None
    companySubcategory: Optional[str] = None
    prevCompanyName: Optional[str] = None
    whetherListedOrNot: Optional[str] = None


class AgentResponse(BaseModel):
    type: Literal["company_details", "general"]

    message: str

    data: Optional[CompanyDetails] = None
