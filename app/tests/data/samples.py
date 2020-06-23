from app.core import config

# Users that will be injected in the test database
users = [
    {
        "id": 1,
        "email": config.FIRST_SUPERUSER,
        "password": config.FIRST_SUPERUSER_PASSWORD,
        "full_name": "admin",
        "is_superuser": True,
        "is_active": True,
    },
    {
        "id": 2,
        "email": config.EMAIL_TEST_USER,
        "password": config.PASS_TEST_USER,
        "full_name": "Test It",
        "is_superuser": False,
        "is_active": True,
    },
    {
        "id": 3,
        "email": "tintin@fastapi.test",
        "password": "Va.phe8L",
        "full_name": "Tintin",
        "is_superuser": False,
        "is_active": True,
    },
    {
        "id": 4,
        "email": "milou@fastapi.test",
        "password": "moo4Mo4Io8op",
        "full_name": "Milou le chien",
        "is_superuser": False,
        "is_active": True,
    },
    {
        "id": 5,
        "email": "haddock@fastapi.test",
        "password": "Gaed/ee6",
        "full_name": "Capitaine Haddock",
        "is_superuser": False,
        "is_active": False,
    },
    {
        "id": 6,
        "email": "castafiore@fastapi.test",
        "password": "Gaed/ee6",
        "full_name": "Bianca Castafiore",
        "is_superuser": False,
        "is_active": False,
    },
    {
        "id": 7,
        "email": "rastapopoulos@fastapi.test",
        "password": "Gaed/ee6",
        "full_name": "Roberto Rastapopoulos",
        "is_superuser": False,
        "is_active": False,
    },
    {
        "id": 8,
        "email": "dupond@fastapi.test",
        "password": "Gaed/ee6",
        "full_name": "Dupond",
        "is_superuser": False,
        "is_active": False,
    },
    {
        "id": 9,
        "email": "dupont@fastapi.test",
        "password": "Gaed/ee6",
        "full_name": "dupont",
        "is_superuser": False,
        "is_active": False,
    },
]

invalid_emails = [
    "",
    " ",
    "plainaddress",
    "#@%^%#$@#$@#.test",
    "@example.test",
    "email.example.test",
    "email@example@example.test",
    ".email@example.test",
    "email.@example.test",
    "email..email@example.test",
    "email@example.test (Joe Smith)",
    "email@example",
    "email@-example.test",
    "email@111.222.333.44444",
    "email@example..test",
    "Abc..123@example.test",
    'this\\ is"really"not\\allowed@example.test',
    # "”(),:;<>[\]@example.test",
    # "あいうえお@example.test",
    # "email@example.web",
    # "just”not”right@example.test",
    # "Joe Smith <email@example.test>",
]

valid_emails = [
    "email@example.test",
    "firstname.lastname@example.test",
    "email@subdomain.example.test",
    "firstname+lastname@example.test",
    "1234567890@example.test",
    "email@example-one.test",
    "_______@example.test",
    "email@example.name",
    "email@example.museum",
    "email@example.co.jp",
    "firstname-lastname@example.test",
    # "email@123.123.123.123",
    # "email@[123.123.123.123]",
    # '"email"@example.test',
    # "much.”more\ unusual”@example.test",
    # "very.unusual.”@”.unusual.test@example.test",
    # 'very.”(),:;<>[]”.VERY.”very@\\ "very”.unusual@strange.example.test',
]

"""Passwords that should be in the *pwned* database"""
corrupted_passwords = [
    # '        ',
    'azerty123',
    # 'qwerty123',
    # '12345678'
]

# Passwords that do follow the restriction.
# Note that we test ascii characters in different langages.
# FIXME: remove it? fixture should depend on the configuration
valid_passwords = [
    # 'ยินดีต้อนรับ-thai-test',
    '-$^/\\+-=%"<>;!?#&-char-test',
    'dtjedvpjpsg-standard-test',
    'lætitia-œuf-ù-french-test',
    'weißbier-german-test',
    'Curlingföräldrar-Mångata-swedish-test',
    '空気読よめない-japanese-test'
    '施氏食獅史-chinese-test',
]

# Passwords that do not follow the restriction
invalid_passwords = [
    '',
    ' ',
    'a',
    'aaaaaaa',
]

invalid_passwords_special = [
    'aaaaaaaa`'
    'zddvldlv°'
]
