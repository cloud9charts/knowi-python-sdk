from knowipy import Knowi

knowi = Knowi(clientId='<your Client ID here>', clientSecret='<your Client Secret here>', flag='mgmt')

# create a user
email = 'awesome.user@knowi.com'
password = 'secret_password'
phone = 1234567890
two_factor = True
user = knowi.users_create(email=email, password=password, phone=phone, twoFA=two_factor)

# list users
user_list = knowi.users_list()
