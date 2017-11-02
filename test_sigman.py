#!/usr/bin/env python3
# Ten skrypt sprawdza działanie wszystkich funkcji pakietu sigman

import sigman as sm
from sigman import file_manager as fm
from sigman import analyzer
from sigman import visualizer as vis
import os

print(">Próba importu próbych .dat")
bp_line = fm.import_line('example_data/BP.dat', line_type = 'bp')
ecg_line = fm.import_line('example_data/EKG.dat', line_type = 'ecg')
r_points = fm.import_points('example_data/R.dat', point_type = 'r') 

print(">Próba połączenia danych w Composite_data")
data_lines={'bp':bp_line, 'ecg':ecg_line}
data_points={'r':r_points}
complete_data = sm.Composite_data(data_lines = data_lines, data_points = data_points)

print(">Próba wizualizacji danych w całości")
vis.visualize_composite_data(complete_data, title="Całość")

print(">Próba wizualizacji wycinka danych")
vis.visualize_composite_data(complete_data, begin_time=60, end_time=80, title="Wycinek dwudziestosekundowy")

print(">Próba wizualizacji wycinka z jedną linią offsetowaną")
complete_data.data_lines['bp'].offset = -0.2
vis.visualize_composite_data(complete_data, begin_time=60, end_time=80, title="Wycinek dwudziestosekundowy z offsetem -0.2s na BP")
complete_data.data_lines['bp'].offset = 0


print(">Próba importu procedury filtrowania")
module = analyzer.import_procedure("filter_butterworth")
print("Procedure type:",module.procedure_type)
print("Description:",module.description)
print("Author:",module.author)
print("Required arguments:",module.required_arguments)

print(">Próba przefiltrowania danych zewnętrzną procedurą filtrowania")
butterworth = analyzer.import_procedure("filter_butterworth")
settings = butterworth.default_settings
settings['N'] = 3
settings['Wn'] = 30
filtered_data_line = analyzer.filter_line(complete_data.data_lines['bp'], 60, 70, butterworth, settings)
complete_data.data_lines['bp'].replace_slice(60, 70, filtered_data_line)
vis.visualize_composite_data(complete_data, begin_time=60, end_time=80, title="Wycinek dwudziestosekundowy po filtracji 30 Hz na zakresie <60s;70s>")

print(">Próba usunięcia zakresu punktów")
complete_data.data_points['r'].delete_slice(65,75)
vis.visualize_composite_data(complete_data, begin_time=60, end_time=80, title="Wycinek dwudziestosekundowy po usunięciu punktów")

print(">Próba zapisania composite_data")
fm.save_composite_data("example_data/example_composite_data.pickle",complete_data)

print(">Proba wczytania innego, bardzo chaotycznego sygnału EKG i przefiltrowania go a następnie pokazania tuż obok nieprzefiltrowanego")
ecg_line = fm.import_line('example_data/EKG_messy.dat', line_type = 'ecg_messy')
settings['N'] = 3
settings['Wn'] = 20
filtered_ecg = analyzer.filter_line(ecg_line, 0, ecg_line.complete_length, butterworth, settings)
complete_data = sm.Composite_data(data_lines={'ecg_messy':ecg_line,'ecg':filtered_ecg})
vis.visualize_composite_data(complete_data, begin_time=10,end_time=15,title="EKG wejściowe (mocno zaburzone) oraz przefiltrowane filtrem 20 Hz")

print(">Próba ponownego wczytania wcześniej zapisanego composite_data")
complete_data = fm.open_composite_data('example_data/example_composite_data.pickle')
vis.visualize_composite_data(complete_data, title="Wczytany ponownie")
os.remove('example_data/example_composite_data.pickle')

#TODO: Odnajdywanie punktów na wykresie
print(">Próba odnalezienia r na odcinku <65s, 75s>")
find_r = analyzer.import_procedure('points_r_simple')
settings = find_r.default_settings
found_points = analyzer.find_points(complete_data, 65, 75, find_r, settings, point_type = 'r')
complete_data.add_data_points(found_points, join=True)
vis.visualize_composite_data(complete_data, begin_time = 60, end_time = 80, title = "Dane z odnalezionymi ponownie R-ami")

print(">Próba usunięcia i odnalezienia wszystkich r")
complete_data.delete_data_points('r')
begin_time, end_time = complete_data.calculate_time_range(required_lines=['ecg'])
found_points = analyzer.find_points(complete_data, begin_time, end_time, find_r, settings, point_type = 'r')
complete_data.add_data_points(found_points)
vis.visualize_composite_data(complete_data, title = "Dane z całkowicie nowymi R-ami")

print(">Próba obliczenia tempa bicia serca na kilku interwałach")
calculate_hr = analyzer.import_procedure('param_heart_rate')
param_tuples = []
for i in range(10,100,10):
    param_tuples.append((i-10,i))
hr = analyzer.calculate_parameter(complete_data, param_tuples ,calculate_hr,
                                  calculate_hr.default_settings, 'hr')
complete_data.add_parameter(hr)
vis.visualize_composite_data(complete_data, begin_time = 0, end_time = 120,
                             title = "Wycinek <0s; 120s> z parametrem")


print(">Próba usunięcia pojedynczego punktu r i zastąpienia go nowym")
vis.visualize_composite_data(complete_data, begin_time = 240, end_time = 243, title = "Wycinek <240s; 243s>")
complete_data.data_points['r'].delete_point(241) #,y=5.8)
x = 241.227
y = complete_data.data_lines['ecg'].value_at(x)
complete_data.data_points['r'].add_point(x,y)
vis.visualize_composite_data(complete_data, begin_time = 240, end_time = 243, title = "Wycinek <240s; 243s> z zamienionym punktem na 241s")

print(">Próba oznaczenia SBP i DBP")
find_sbp = analyzer.import_procedure('points_sbp_simple')
settings = find_sbp.default_settings
begin_time, end_time = complete_data.calculate_time_range(required_lines=['bp'])
found_sbp = analyzer.find_points(complete_data, begin_time, end_time, find_sbp, settings, point_type = 'sbp')
complete_data.add_data_points(found_sbp)
find_dbp = analyzer.import_procedure('points_dbp_simple')
settings = find_dbp.default_settings
begin_time, end_time = complete_data.calculate_time_range(required_lines=['bp'])
found_dbp = analyzer.find_points(complete_data, begin_time, end_time, find_dbp, settings, point_type = 'dbp')
complete_data.add_data_points(found_dbp)
vis.visualize_composite_data(complete_data, title="Dane z odnalezionymi SBP i DBP")

print(">Próba oznaczenia DN")
find_dn = analyzer.import_procedure('points_dn_net')
settings = find_dn.default_settings
begin_time, end_time = complete_data.calculate_time_range(required_lines=['ecg','bp'])
found_dn = analyzer.find_points(complete_data, begin_time, end_time, find_dn, settings, point_type = 'dn')
complete_data.add_data_points(found_dn)
vis.visualize_composite_data(complete_data, title="Dane z odnalezionymi DN")