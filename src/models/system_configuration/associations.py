from sqlalchemy import Column, ForeignKey, Integer, Table

from db.db import Base

# Таблица связи Enquiry <-> EnquiryTemplate
enquiry_enquiry_template_table = Table(
    "enquiry_enquiry_template",
    Base.metadata,
    Column(
        "enquiry_id",
        Integer,
        ForeignKey("system_configuration.enquiry.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "enquiry_template_id",
        Integer,
        ForeignKey(
            "system_configuration.enquiry_template.id", ondelete="CASCADE"
        ),
        primary_key=True,
    ),
    schema="system_configuration",
)

# Таблица связи EnquiryTemplate <-> EnquiryTemplateBlock
enquiry_template_block_association_table = Table(
    "enquiry_template_enq_template_block",
    Base.metadata,
    Column(
        "enquiry_template_id",
        Integer,
        ForeignKey(
            "system_configuration.enquiry_template.id", ondelete="CASCADE"
        ),
        primary_key=True,
    ),
    Column(
        "enquiry_template_block_id",
        Integer,
        ForeignKey(
            "system_configuration.enquiry_template_block.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    schema="system_configuration",
)

# Таблица связи EnquiryTemplateBlock <-> Query
enquiry_template_block_query_association_table = Table(
    "enquiry_template_block_query",
    Base.metadata,
    Column(
        "enquiry_template_block_id",
        Integer,
        ForeignKey(
            "system_configuration.enquiry_template_block.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "query_id",
        Integer,
        ForeignKey("page_configuration.query.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    schema="system_configuration",
)

# Таблица связи user <-> user_data
user_user_data_association_table = Table(
    "user_user_data",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("access_control.user.id"),
        primary_key=True,
    ),
    Column(
        "user_data_id",
        Integer,
        ForeignKey("access_control.user_data.id"),
        primary_key=True,
    ),
    schema="access_control",
)
