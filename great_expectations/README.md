great_expectations init
great_expectations suite new : first draft
great_expectations suite edit : edit the suitenusing jupyter
great_expectations docs build --site-name local_site
great_expectations docs build --site-name gs_site 

expect_column_to_exist
expect_table_row_count_to_be_between
expect_column_values_to_be_unique
expect_column_values_to_not_be_null
expect_column_values_to_be_between
expect_column_values_to_match_regex
expect_column_mean_to_be_between
expect_column_kl_divergence_to_be_less_than
... and many more : https://docs.greatexpectations.io/en/latest/reference/glossary_of_expectations.html?utm_source=walkthrough&utm_medium=glossary

example : 
```
{
    "expectation_type": "expect_column_values_to_not_be_null",
    "kwargs": {
        "column": "user_id"
    }
}
```