import whois
import datetime
import requests
import argparse
import re
import calendar


def load_urls4check(path):
    urls = []
    with open(path, 'r') as f:
        line = f.readlines()
        for item in line:
            item = re.sub('\n', '', item)
            urls.append(item)
    return urls


def get_http_status_code(urls):
    status_code = []
    for item in urls:
        response = requests.get(item)
        if response.status_code == 200:
            status_code.append('status OK')
        else:
            status_code.append(response.status_code)
    return status_code


def get_domain_from_url(urls):
    domain_name = []
    for item in urls:
        domain_name.append(re.sub('http://www.|http://', '', item))
    return domain_name


def get_domain_expiration_date(domain_name):
    exp_date = []
    for item in domain_name:
        who_is = whois.whois(item)
        expiration_date = who_is.expiration_date
        if type(expiration_date) == list:
            exp_date.append(expiration_date[0])
        else:
            exp_date.append(expiration_date)
    return exp_date


def deadline_test(exp_date):
    lifetime = []
    today = datetime.date.today()
    this_year = int(datetime.datetime.strftime(today, "%Y"))
    this_month = int(datetime.datetime.strftime(today, "%m"))
    days_in_this_month = calendar.monthrange(this_year, this_month)[1]
    deadline = datetime.timedelta(days=days_in_this_month)
    for item in exp_date:
        if item:
            delta = item.date() - today
            if delta >= deadline:
                lifetime.append('expiration date greater than 1 month')
            else:
                lifetime.append('expiration date less than 1 month')
        else:
            lifetime.append('expiration date is not defined')
    return lifetime


def get_report(urls, http_status, deadline):
    report = dict(zip(urls, zip(http_status, deadline)))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='help',
                        help='Справка')
    parser.add_argument('-f', '--filename', type=str,
                        help='Файл со списком проверяемых сайтов')
    args = parser.parse_args()
    if not args.filename:
        print('не указан файл с адресами проверяемых сайтов')
        exit()
    else:
        urls = load_urls4check(args.filename)
    domain_name = get_domain_from_url(urls)
    exp_date = get_domain_expiration_date(domain_name)
    http_status = get_http_status_code(urls)
    lifetime = deadline_test(exp_date)
    report = get_report(urls, http_status, lifetime)
    for key in report.keys():
        print(key, report[key])
