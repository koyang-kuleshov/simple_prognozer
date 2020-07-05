import requests
import pandas as pd
from github.MainClass import Github
'''
GIT_TOKEN = '9ac1fcab6da1407b3d6d5a687f4093de0f79d422'
REPOSITORY_PATH = 'CSSEGISandData/COVID-19'

DAILY_REPORTS_FILE_LIST = 'csse_covid_19_data/csse_covid_19_daily_reports'

token = '952d6b2c5667ad09b38d798a3f98bf27289de9f6'
repo_path = 'CSSEGISandData/COVID-19'
daily_reports_dir_path = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_daily_reports/'
time_series_dir_path = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/'
dr_repo_file_list = 'csse_covid_19_data/csse_covid_19_daily_reports'

git = Github(token)
repo = git.get_repo(repo_path)
daily_reports_file_list = repo.get_contents(dr_repo_file_list)[1:-1]
df_result = pd.DataFrame(columns=['Last_Update',
                                  'FIPS',
                                  'Admin2',
                                  'Province_State',
                                  'Country_Region',
                                  'Lat',
                                  'Long_',
                                  'Confirmed',
                                  'Deaths',
                                  'Recovered',

                                  ])
for report in daily_reports_file_list:
    df = pd.read_csv(report.download_url)
    print(report)
    if {'Last Update'}.issubset(df.columns):
        df.rename(
            columns={'Latitude': 'Lat', 'Longitude': 'Long_',
                     'Province/State': 'Province_State',
                     'Country/Region': 'Country_Region',
                     'Last Update': 'Last_Update'},
            inplace=True)

    df_result = pd.concat([df_result, df])

df_result.to_csv('converted.csv')
'''
df_result = pd.read_csv('converted.csv')

# исправляем разные названия одной страны
df_result.loc[df_result['Country_Region'] == 'Mainland China', 'Country_Region'] = 'China'
df_result.loc[df_result['Country_Region'] == ' Azerbaijan', 'Country_Region'] = 'Azerbaijan'
df_result.loc[df_result['Country_Region'] == 'Gambia, The', 'Country_Region'] = 'Gambia'
df_result.loc[df_result['Country_Region'] == 'Hong Kong SAR', 'Country_Region'] = 'China'
df_result.loc[df_result['Country_Region'] == 'Hong Kong', 'Country_Region'] = 'China'
df_result.loc[df_result['Country_Region'] == 'Iran (Islamic Republic of)', 'Country_Region'] = 'Iran'
df_result.loc[df_result['Country_Region'] == 'South Korea', 'Country_Region'] = 'Korea, South'
df_result.loc[df_result['Country_Region'] == 'Republic of Korea', 'Country_Region'] = 'Korea, South'
df_result.loc[df_result['Country_Region'] == 'Russian Federation', 'Country_Region'] = 'Russia'
df_result.loc[df_result['Country_Region'] == 'UK', 'Country_Region'] = 'United Kingdom'
df_result.loc[df_result['Country_Region'] == 'Taiwan', 'Country_Region'] = 'Taiwan*'
# исправляем разные форматы дат
df_result['Last_Update'] = pd.to_datetime(df_result['Last_Update'])
df_result['Last_Update'] = df_result['Last_Update'].apply(lambda x: x.date())

df_result = df_result.drop_duplicates(subset=['FIPS', 'Admin2', 'Country_Region', 'Province_State', 'Last_Update'], keep=False)

df_result.to_csv('result.csv')

df_by_date = df_result.groupby(['Last_Update']).sum().reset_index(drop=None)
df_by_date.to_csv('total.csv')

df_by_country = df_result.groupby(['Last_Update', 'Country_Region'])[['Confirmed', 'Deaths', 'Recovered']].sum()
print(df_by_country.head())
df_by_country = df_by_country.groupby(['Country_Region']).max()
df_by_country.to_csv('country.csv')



# df_confirmed = pd.read_csv('csv/time_series_covid19_confirmed_global.csv')
# df_deaths = pd.read_csv('csv/time_series_covid19_deaths_global.csv')
# df_recovered = pd.read_csv('csv/time_series_covid19_recovered_global.csv')
# df_confirmed_us = pd.read_csv('csv/time_series_covid19_confirmed_US.csv')
# df_confirmed_us = pd.DataFrame(
#     df_confirmed_us.groupby(['Province_State']).sum()
#                                ).reset_index()
# df_deaths_us = pd.read_csv('csv/time_series_covid19_deaths_US.csv')
# df_deaths_us = pd.DataFrame(
#     df_deaths_us.groupby(['Province_State']).sum()
#                             ).reset_index()
#
# df_confirmed_convert = pd.DataFrame(columns=['ObservationDate',
#                                              'Province/State',
#                                              'Country/Region',
#                                              'Confirmed'
#                                              ])
# for row_num in range(len(df_confirmed)):
#     df_temp = df_confirmed.loc[row_num]
#
#     df_confirmed_convert = df_confirmed_convert.append(
#         pd.DataFrame({
#             'ObservationDate': df_temp.iloc[4:].index,
#             'Province/State': df_temp['Province/State'],
#             'Country/Region': df_temp['Country/Region'],
#             'Confirmed': df_temp.iloc[4:].values,
#         }),
#         ignore_index=True)
#
# df_deaths_convert = pd.DataFrame(columns=['ObservationDate',
#                                           'Province/State',
#                                           'Country/Region',
#                                           'Deaths'
#                                           ])
# for row_num in range(len(df_deaths)):
#     df_temp = df_deaths.loc[row_num]
#
#     df_deaths_convert = df_deaths_convert.append(
#         pd.DataFrame({
#             'ObservationDate': df_temp.iloc[4:].index,
#             'Province/State': df_temp['Province/State'],
#             'Country/Region': df_temp['Country/Region'],
#             'Deaths': df_temp.iloc[4:].values,
#         }),
#         ignore_index=True)
#
# df_recovered_convert = pd.DataFrame(columns=['ObservationDate',
#                                              'Province/State',
#                                              'Country/Region',
#                                              'Recovered'
#                                              ])
# for row_num in range(len(df_recovered)):
#     df_temp = df_deaths.loc[row_num]
#
#     df_recovered_convert = df_recovered_convert.append(
#         pd.DataFrame({
#             'ObservationDate': df_temp.iloc[4:].index,
#             'Province/State': df_temp['Province/State'],
#             'Country/Region': df_temp['Country/Region'],
#             'Recovered': df_temp.iloc[4:].values,
#         }),
#         ignore_index=True)
#
# # df_confirmed_us_convert = pd.DataFrame(columns=['ObservationDate',
# #                                                 'Province/State',
# #                                                 'Country/Region',
# #                                                 'Confirmed'
# #                                                 ])
# #
# # for row_num in range(len(df_confirmed_us)):
# #     df_temp = df_confirmed_us.loc[row_num]
# #
# #     df_confirmed_us_convert = df_confirmed_us_convert.append(
# #         pd.DataFrame({
# #             'ObservationDate': df_temp.iloc[6:].index,
# #             'Province/State': df_temp['Province_State'],
# #             'Country/Region': 'US',
# #             'Confirmed': df_temp.iloc[6:].values,
# #         }),
# #         ignore_index=True)
# #
# # df_deaths_us_convert = pd.DataFrame(columns=['ObservationDate',
# #                                              'Province/State',
# #                                              'Country/Region',
# #                                              'Deaths'
# #                                              ])
# #
# # for row_num in range(len(df_deaths_us)):
# #     df_temp = df_deaths_us.loc[row_num]
# #
# #     df_deaths_us_convert = df_deaths_us_convert.append(
# #         pd.DataFrame({
# #             'ObservationDate': df_temp.iloc[7:].index,
# #             'Province/State': df_temp['Province_State'],
# #             'Country/Region': 'US',
# #             'Deaths': df_temp.iloc[7:].values,
# #         }),
# #         ignore_index=True)
#
# # result_df = df_confirmed_convert.merge(
# #     df_deaths_convert.merge(
# #         df_recovered_convert.merge(
# #             df_confirmed_us_convert.merge(
# #                 df_deaths_us_convert,
# #                 how='outer'),
# #             how='outer'),
# #         how='outer'),
# #     how='outer',
# # )
#
# result_df = df_confirmed_convert.merge(
#     df_deaths_convert.merge(
#         df_recovered_convert,
#             how='outer'),
#         how='outer')
# result_df.to_csv('converted.csv')

