import whois
import datetime
import requests
import argparse
import re
import calendar

# http://edu-top.ru/katalog/urls.php


def load_urls4check(path):
    urls = []
    with open(path, 'r') as f:
        line = f.readlines()
        for item in line:
            item = re.sub('\n', '', item)
            urls.append(item)
    return urls


def is_server_respond_with_200(urls):
    status = []
    for item in urls:
        response = requests.get(item)
        status_code = response.status_code
        if status_code == 200:
            status.append('status : OK')
        else:
            status.append('status : False')
    return status


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


def prepare_to_print_result(urls, url_status, deadline):
    dct_of_results = dict(zip(urls, zip(url_status, deadline)))
    return dct_of_results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='help',
                        help='show this message and exit')
    parser.add_argument('-f', '--filename', type=str,
                        help='Файл со списком проверяемых сайтов')
    args = parser.parse_args()
    if not args.filename:
        print ('нет такого файла')
    else:
        urls = load_urls4check(args.filename)
    domain_name = get_domain_from_url(urls)
    exp_date = get_domain_expiration_date(domain_name)
    url_status = is_server_respond_with_200(urls)
    lifetime = deadline_test(exp_date)
    report = prepare_to_print_result(urls, url_status, lifetime)
    for key in report.keys():
        print (key, report[key])
