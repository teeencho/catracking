"""
When dealing with Measurement Protocol all events must be defined in this block
with proper docstring, explaining why was it created, possible values and when
the event is triggered.

"""

"""
Category for all events related to a brand interaction
"""

EVENT_CATEGORY_BRAND_INTERACTION = 'brand interaction'

"""
`submit lead` event

Label is dynamic according to the brand name.
"""

EVENT_ACTION_SUBMIT_LEAD = 'submit lead'

"""
Category for all events related to a verified lead.
The event action is dynamic (campaign name)

"""

EVENT_CATEGORY_VERIFIED_LEAD = 'verified lead'

"""
Labels for the verified lead event, can be either `click`, `call` or `form`.

"""
EVENT_LABEL_CLICK = 'click'
EVENT_LABEL_CALL = 'call'
EVENT_LABEL_FORM = 'form'

"""
Category for all events related to accounts: login, registration, password.

"""
EVENT_CATEGORY_ACCOUNT = 'customer account'


"""
Login events (for email login only).

Works for both legacy and new design.

Used values:
    fail: triggered when login form is submitted with invalid credentials
          (POST method for accounts.views.LoginViewBase)
    success: triggered when login form is submitted with valid credentials
             (POST method for accounts.views.LoginViewBase)

"""
EVENT_ACTION_LOGIN = 'sign-in account'
EVENT_ACTION_SOCIAL_LOGIN = 'sign-in social account'


"""
Registration events (for email registration only).

Works only for new design.

Used values:
    fail: triggered when registration form is submitted with invalid data
          (POST method for accounts.views.CreateAccountViewV2)
    success: triggered when registration form is submitted with valid data
             (POST method for accounts.views.CreateAccountViewV2)

"""
EVENT_ACTION_REGISTRATION = 'create account'
EVENT_ACTION_SOCIAL_REGISTRATION = 'create social account'


"""
Password reset request events.

Works only for new design.

Used values:
    fail: triggered when password reset request form is submitted
          with invalid data. Unable to trigger from the FE since
          JS validations don't allow for invalid data to be sent to the BE.
          (POST method for misc.password.PasswordResetView)
    success: triggered when password reset request form is submitted
             with valid data (POST method for misc.password.PasswordResetView)

"""
EVENT_ACTION_PASSWORD_REQUEST = 'password reset request'


"""
Password reset change events.

Works only for new design.

Used values:
    fail: triggered when password reset change form is submitted
          with invalid data
          (POST method for misc.password.PasswordResetConfirmView)
    success: triggered when password reset change form is submitted
             with valid data
             (POST method for misc.password.PasswordResetConfirmView)

"""
EVENT_ACTION_PASSWORD_CHANGE = 'password reset change'


"""
Category for all events related to affiliates.

The action for this events is the affiliate name.

The label for this events is the affiliate link.

"""
EVENT_CATEGORY_AFFILIATE_EVENT = 'affiliate'


"""
Maps the source from the url of the affiliate redirect URL, to the
corresponding field.

Used values:
    amazon: triggered when Amazon affiliate link is clicked from the
            categories page (as of writting, only for unaccredited profiles).

"""
EVENT_ACTION_AFFILIATE_MAP = {'amazon': 'amazon_affiliate_category'}

"""
Category for all events related to a pdf download.

The action for this event is the pdf filename.

The label for this event is the page the pdf was downloaded from.

"""

EVENT_CATEGORY_PDF_DOWNLAOD = 'pdf download'


"""
Category for all events related to careers.
"""
EVENT_CATEGORY_CAREERS = 'careers'

"""
Application submission action.

Label can be either `success` or `fail`
"""
EVENT_ACTION_SUBMIT_APPLICATION = 'submit application'

"""
Category for all events related to matching tool
"""

EVENT_CATEGORY_MATCHING_TOOL = 'matching tool'

EVENT_ACTION_BRAND_CALL_ME_NOW = 'brand call me now'
