from knowipy import Knowi

# instantiate Knowi client
knowi = Knowi(customerToken='<KNOWI_CUSTOMER_TOKEN>', flag='sso')

# --------
# list all sub-customers within a parent customer
customers = knowi.sso_listSubCustomers()

# create a sub-customer with a customer content filter and shared group from the parent customer
sub_customer_group = knowi.sso_createSubCustomer(subCustomerEmail='admin@acme.com', subCustomerName='Acme Bakery',
                                                 groups=["Bakers Dozen", "Pastry"],
                                                 subCustomerFilters=[
                                                     {"fieldName": "orgId", "values": [123, 7893], "operator": "="}])
print(sub_customer_group)

# --------
# create a sub-customer with a custom role from the parent customer
# this copies a custom role from the parent customer to the sub customer
sub_customer_roles = knowi.sso_createSubCustomer(subCustomerEmail='admin@acme.com', subCustomerName='Acme Bakery',
                                                 roles=["Managers"])

print(sub_customer_group)

# --------
# update sub-customer name and roles from parent customer
# with overWriteRoles=True, any changes to Managers will be reflected in the sub customer account
update_customer = knowi.sso_updateSubCustomer(subCustomerToken="r7kRqAkrisNZ7VVk9pk9pPdNApIcyWtKVSGORVpSczLMie",
                                              subCustomerName="Acme's Bakery", roles=["Managers"],
                                              overwriteRoles=True)
print(update_customer)

# --------
# associate/disassociate a sub-customer user to a parent customer group
# this will remove any groups previously attached to this user and assign user to groups: "Pie" and "Cake"
update_user_group = knowi.sso_updateSubCustomer(subCustomerToken="r7kRqAkrisNZ7VVk9pk9pPdNApIcyWtKVSGORVpSczLMie",
                                                email="admin@acme.com", groups=["Pie", "Cake"])
print(update_user_group)
