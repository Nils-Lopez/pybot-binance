from github import Github


def saveOrder (time, slorder, tporder, order, token):
    print(f'Saving order : {order}');
    github = Github(token)

    repository = github.get_user().get_repo('ocTrader-data')
    filename = f'orders/{time}.json'

    content = (f'ORDER : {order}, STOP-LOSS: {slorder}, TAKEPROFIT: {tporder}')

    f = repository.create_file(filename, "new order from OctoPyBot using pyGithub", content)

    print(f'repo : {repository}')