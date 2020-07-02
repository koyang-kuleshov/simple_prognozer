from github.MainClass import Github
import requests

GIT_TOKEN = '9ac1fcab6da1407b3d6d5a687f4093de0f79d422'
REPOSITORY_PATH = 'CSSEGISandData/COVID-19'

DAILY_REPORTS_FILE_LIST = 'csse_covid_19_data/csse_covid_19_daily_reports'

TIME_SERIES_FILE_LIST = 'csse_covid_19_data/csse_covid_19_time_series'


def get_csv(file_name):
    token = ''  # GitHub TOKEN

    repo_path = 'CSSEGISandData/COVID-19'
    daily_reports_dir_path = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_daily_reports/'
    time_series_dir_path = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/'
    dr_repo_file_list = 'csse_covid_19_data/csse_covid_19_daily_reports'

    git = Github(token)
    repo = git.get_repo(repo_path)
    daily_reports_file_list = repo.get_contents(dr_repo_file_list)

    if file_name == 'daily_reports':
        daily_reports_file_path = daily_reports_dir_path + str(daily_reports_file_list[-2]).split('/')[-1].split(".")[0] + '.csv'
        req = requests.get(daily_reports_file_path)
        url_content = req.content
        csv_file = open('daily_report.csv', 'wb')
        csv_file.write(url_content)
        csv_file.close()
    else:
        confirmed_global_file_path = time_series_dir_path + 'time_series_covid19_confirmed_global.csv'
        deaths_global_file_path = time_series_dir_path + 'time_series_covid19_deaths_global.csv'
        recovered_global_file_path = time_series_dir_path + 'time_series_covid19_recovered_global.csv'
        return confirmed_global_file_path, deaths_global_file_path, recovered_global_file_path