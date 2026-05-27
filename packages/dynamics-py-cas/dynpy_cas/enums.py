from django.db import models
from django.utils.translation import gettext_lazy as _


class Codename(models.TextChoices):
    AGING_ADMIN = ("ext_aging_admin", _("Aging Admin"))
    AGING_EDITOR = ("ext_aging_editor", _("Aging Editor"))
    AGING_USER = ("ext_aging_user", _("Aging User"))
    AUTHORIZATIONS_ADMIN = ("ext_authorizations_admin", _("Authorizations Admin"))
    AUTHORIZATIONS_EDITOR = ("ext_authorizations_editor", _("Authorizations Editor"))
    AUTHORIZATIONS_USER = ("ext_authorizations_user", _("Authorizations User"))
    BILLING_CALENDAR_ADMIN = ("ext_billing_calendar_admin", _("Billing Calendar Admin"))
    BILLING_CALENDAR_EDITOR = ("ext_billing_calendar_editor", _("Billing Calendar Editor"))
    BILLING_CALENDAR_USER = ("ext_billing_calendar_user", _("Billing Calendar User"))
    CALLFIRE_ADMIN = ("ext_callfire_admin", _("Callfire Admin"))
    CALLFIRE_EDITOR = ("ext_callfire_editor", _("Callfire Editor"))
    CALLFIRE_USER = ("ext_callfire_user", _("Callfire User"))
    CAS_ADMIN = ("ext_cas_admin", _("CAS Admin"))
    CAP_EDITOR = ("ext_cap_editor", _("CAP Editor"))
    CAP_USER = ("ext_cap_user", _("CAP User"))
    DOCUMENT_PROCESSING_USER = ("ext_document_processing_user", _("Document Processing User"))
    DOCUMENT_PROCESSING_EDITOR = ("ext_document_processing_editor", _("Document Processing Editor"))
    DOCUMENT_PROCESSING_TEN_95 = ("ext_document_processing_ten_95", _("1095"))
    DOCUMENT_PROCESSING_OVERTIME = ("ext_document_processing_overtime", _("Overtime"))
    FACILITY_CONFIG_READ_ONLY = ("ext_facility_config_read_only", _("Facility Config Read Only"))
    FACILITY_CONFIG_EDITOR = (
        "ext_facility_config_editor",
        _("Facility Config Editor"),
    )
    FACILITY_CONFIG_USER = (
        "ext_facility_config_user",
        _("Facility Config User"),
    )
    HMO_BILLING_ADMIN = ("ext_hmo_billing_admin", _("HMO Billing Admin"))
    HMO_BILLING_EDITOR = ("ext_hmo_billing_editor", _("HMO Billing Editor"))
    HMO_BILLING_USER = ("ext_hmo_billing_user", _("HMO Billing User"))
    HMO_BILLING_PHARMACY_USER = ("ext_hmo_billing_pharmacy_user", _("HMO Billing Pharmacy User"))
    MEDICAID_ADMIN = ("ext_medicaid_admin", _("Medicaid Admin"))
    MEDICAID_EDITOR = ("ext_medicaid_editor", _("Medicaid Editor"))
    MEDICAID_USER = ("ext_medicaid_user", _("Medicaid User"))
    TRACKING_ADMIN = ("ext_tracking_admin", _("Tracking Admin"))
    TRACKING_REQUEST_COORDINATOR = (
        "ext_tracking_request_coordinator",
        _("Tracking Request Coordinator"),
    )
    TRACKING_EDITOR = ("ext_tracking_editor", _("Tracking Editor"))
    TRACKING_USER = ("ext_tracking_user", _("Tracking User"))
    VENDOR_SEARCH_USER = ("ext_vendor_search_user", _("Vendor Search User"))
    VENDOR_SEARCH_EDITOR = ("ext_vendor_search_editor", _("Vendor Search Editor"))
    LEP_USER = ("ext_lep_user", _("Logging Error Platform User"))
    HAS_MFA_METHOD = ("ext_has_mfa_method", _("Has MFA Method"))
    SURVEYS_ADMIN = ("ext_surveys_admin", _("Surveys Admin"))
    SURVEYS_EDITOR = ("ext_surveys_editor", _("Surveys Editor"))
    SURVEYS_USER = ("ext_surveys_user", _("Surveys User"))
    PAYROLL_ALLOCATIONS_ADMIN = ("ext_payroll_allocations_admin", _("Payroll Allocations Admin"))
    PAYROLL_ALLOCATIONS_EDITOR = ("ext_payroll_allocations_editor", _("Payroll Allocations Editor"))
    PAYROLL_ALLOCATIONS_USER = ("ext_payroll_allocations_user", _("Payroll Allocations User"))
