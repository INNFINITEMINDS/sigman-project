* [Wstęp](https://github.com/k-cybulski/sigman-project#sigman-project)
* [Instalacja](https://github.com/k-cybulski/sigman-project#instalacja)
  * [Technologie i biblioteki](https://github.com/k-cybulski/sigman-project#technologie-i-biblioteki)
  * [Linux](https://github.com/k-cybulski/sigman-project#linux)
    * [Ubuntu](https://github.com/k-cybulski/sigman-project#ubuntu)
* [Obsługa](https://github.com/k-cybulski/sigman-project#obs%C5%82uga)
  * [QtSigman](https://github.com/k-cybulski/sigman-project#qtsigman)
  * [sigman](https://github.com/k-cybulski/sigman-project#sigman)
    * [sigman.Wave](https://github.com/k-cybulski/sigman-project#sigmanwave)
    * [sigman.Points](https://github.com/k-cybulski/sigman-project#sigmanpoints)
    * [sigman.Parameter](https://github.com/k-cybulski/sigman-project#sigmanparameter)
    * [sigman.Composite_data](https://github.com/k-cybulski/sigman-project#sigmancomposite_data)
    * [sigman.visualizer](https://github.com/k-cybulski/sigman-project#sigmanvisualizer)
    * [sigman.analyzer](https://github.com/k-cybulski/sigman-project#sigmananalyzer)
    * [Filtracja / modyfikacja przebiegu](https://github.com/k-cybulski/sigman-project#filtracja--modyfikacja-przebiegu)
    * [Odnajdywanie punktów](https://github.com/k-cybulski/sigman-project#odnajdywanie-punkt%C3%B3w)
    * [Obliczanie parametrów](https://github.com/k-cybulski/sigman-project#obliczanie-parametr%C3%B3w)
* [Stan obecny](https://github.com/k-cybulski/sigman-project#stan-obecny)
  * [sigman](https://github.com/k-cybulski/sigman-project#sigman-1)
  * [QtSigman](https://github.com/k-cybulski/sigman-project#qtsigman-1)
* [Standardy kodu](https://github.com/k-cybulski/sigman-project#standardy-kodu)
* [Podziękowania](https://github.com/k-cybulski/sigman-project#podzi%C4%99kowania)

# sigman-project
Celem tego projektu jest utworzenie otwartej i dobrze udokumentowanej biblioteki **sigman** pozwalającej na dowolną analizę danych biomedycznych w formie wielokanałowych sygnałów cyfrowych za pomocą prostych do utworzenia zewnętrznych procedur, a także aplikacji **QtSigman** która pozwoli na korzystanie z tej biblioteki przez interfejs graficzny.

## Instalacja
### Technologie i biblioteki
* [Python 3](https://www.python.org/about/) - całość
* [NumPy](http://www.numpy.org/) - podstawowa obsługa danych
* [SciPy](https://scipy.org/) - filtry/dodatkowe funkcje do analizy
* [matplotlib](http://matplotlib.org/) - wizualizacja wykresów
* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI
* [XlsxWriter](https://github.com/jmcnamara/XlsxWriter) - Zapisywanie plików .xlsx

### Linux
#### Ubuntu
```
git clone "https://github.com/k-cybulski/sigman-project.git"
sudo apt install python3-pip
pip3 install PyQt5 numpy scipy matplotlib XlsxWriter
```

## Obsługa
### QtSigman
Należy uruchomić skrypt `run_qtsigman.py`.

### sigman
Poniższe przykłady zakładają importowanie `sigman` jako `sm`, a `sigman.file_manager` jako `fm`.

#### sigman.Wave
Podstawowym rodzajem danych w bibliotece sigman jest przebieg `sigman.Wave` (*z ang. waveform*) . Określony jest on przede wszystkim tablicą danych `Wave.data` oraz całkowitym czasem trwania `Wave.complete_length`. Z liczby danych oraz ich długości w czasie obliczana jest częstotliwość samplowania `Wave.sample_rate`, oraz długość sampla `Wave.sample_length`. Do późniejszej analizy ważny będzie także typ przebiegu `Wave.type` określający rodzaj danych, np. `ecg` czy `bp`.

Inicjalizacja `sigman.Wave` zawierającego wartości funkcji sinus od 0 do 4pi na umownej przestrzeni 10 sekund.
```python
import sigman as sm
import numpy as np
sine = np.sin(np.linspace(0, 4*np.pi))
sine_wave = sm.Wave(sine, 10, 'sine')
```

Obiekty `sigman.Wave` można importować za pomocą funkcji `file_manager.import_wave`.
```python
from sigman import file_manager as fm
ecg = fm.import_wave('example_data/EKG.dat', 'ecg')
```

W wypadku rozsynchronizowania przebiegu względem innych w czasie ważna jest też zmienna `Wave.offset` pozwalająca korygować takie błędy przez przesuwanie przebiegu.

Podstawową metodą pobierania informacji z `sigman.Wave` jest `Wave.data_slice`, która zwraca tablicę wartości danych na danym zakresie czasowywm. Dokładniejsza dokumentacja w `sigman/__init__.py`. Kilka przykładów:
```python
>>> ecg.data_slice(5, 5.025) # 25 milisekundowy wycinek przebiegu
array([ 0.10659864,  0.10404629,  0.1673287 ,  0.1688633 ,  0.04704312])
>>> ecg.data_slice(5, 8, value_every=1) # wycinek wartości przebiegu na przestrzeni 3 sekund oddalonych o 1 sekundę od siebie
array([ 0.10659864, -0.52108215,  0.95624742])
>>> ecg.data_slice(5, 25, value_count=5) # wycinek 5 wartości na przestrzeni 20 sekund
array([ 0.10659864,  0.35472794, -0.61547362, -0.75704451, -0.59674523])
```

#### sigman.Points
Punkty oznaczające wydarzenia w czasie o danej wartości, np. R na przebiegu EKG, symbolizowane są klasą `sigman.Points`. Zawiera on dwie tablice `Points.data_x` oraz `Points.data_y` posortowane w kolejności `data_x`, a także typ punktów jak `r`.

Inicjalizacja kilku punktów.
```python
import sigman as sm
data_x = [1, 4, 7]
data_y = [3, -2, 4]
points = sm.Points(data_x, data_y, 'example')
```

Punkty można importować
```python
from sigman import file_manager as fm
r = fm.import_points('example_data/R.dat', 'r')
```
lub odnajdywać za pomocą procedur, co zostanie wytłumaczone dogłębniej potem.

Podobnie jak przy `sigman.Wave` jest metoda `Points.data_slice`.
```python
>>> r.data_slice(20,23)
(array([ 20.61868,  21.49193,  22.3552 ]), array([ 4.07120371,  3.76066208,  3.69650602]))
```

#### sigman.Parameter
Klasa zawierająca tablice obliczonych wartości `Parameter.values` parametru, np. częstotliwości bicia serca, a także informacje o tym od jakiego czasu `Parameter.begin_times`  do jakiego `Parameter.end_times` są one obliczone. Tworzy się je tylko wykorzystując procedury.

#### sigman.Composite_data
Klasa łącząca kilka powyższych danych w jedną spójną całość. Może zawierać nieokreśloną liczbę `sigman.Wave`, `sigman.Points` oraz `sigman.Parameter` w trzech `dict`. Pozwala dzięki temu stosować procedury korzystające z kilku kanałów danych, np. procedurę odnajdującą wcięcia dykrotyczne w oparciu o SBP i przebiegi BP oraz EKG. Procedury pobierają dane przez bezpośrednie odwołania do `dict` danych, np. `composite_data.waves['ecg']`. Te trzy `dict` to:
* `Composite_data.waves`
* `Composite_data.points`
* `Composite_data.parameters`

Dodawać je można i przy inicjalizacji i już po zainicjalizowaniu.
```python
import sigman as sm
from sigman import file_manager as fm

ecg = fm.import_wave('example_data/EKG.dat', 'ecg')
composite_data = sm.Composite_data(waves={'ecg':ecg}) # przy inicjalizacji

bp = fm.import_wave('example_data/BP.dat', 'bp')
composite_data.add_wave(bp, 'bp') # po inicjalizacji
r = fm.import_points('example_data/R.dat', 'r')
composite_data.add_points(r, 'r')
```

`file_manager` zawiera też funkcje pozwalające zapisywać `sigman.Composite_data` na potem.
```python
fm.save_composite_data('temporary_save.pickle', composite_data)
```
oraz
```python
composite_data = fm.load_composite_data('temporary_save.pickle')
```

Obecnie wykorzystuje to moduł pythonowy `pickle`, choć jest w planach w przyszłości zamienić go na coś bezpieczniejszego.

#### sigman.visualizer
Biblioteka sigman zawiera moduł `visualizer` pozwalający na bardzo proste lecz dość ograniczone wizualizowanie `sigman.Composite_data`. Po wykonaniu powyższego kodu tworzącego composite_data można spróbować:
```python
from sigman import visualizer as vis
vis.visualize_composite_data(composite_data)
```
`visualizer` pozwala także na wizualizację tylko wycinka czasowego, czy też tylko wybranych danych z `sigman.Composite_data`.
```python
vis.visualize_composite_data(composite_data, begin_time=40, end_time=60, 
                             wanted_waves=['ecg'], title="Wykres EKG") 
```

#### sigman.analyzer
Moduł `analyzer` pozwala na stosowanie zewnętrznych procedur z folderu `sigman-project/procedures` na danych. Ich dokładna struktura i całokształt opisany jest głębiej w samym pliku modułu.

Zakładany sposób wykorzystania procedur polega na zaimportowaniu ich funkcją `analyzer.import_procedure`, zmodyfikowaniu wybranych argumentów z `procedure.default_arguments`, zaaplikowaniu jej przez odpowiednią funkcję z `sigman.analyzer` a następnie zamiany danych w `sigman.Composite_data` na nowe.

##### Filtracja / modyfikacja przebiegu
Filtrację / modyfikację przebiegu możemy przeprowadzić importując procedurę typu `modify` i następnie aplikując ją korzystając z funkcji `analyzer.modify_wave`. Funkcja ta przyjmuje `sigman.Wave` do modyfikacji, początek i koniec zakresu czasowego na jakim należy przeprowadzić procedurę, zaimportowany moduł procedury oraz `dict` argumentów oparty na `procedure.default_arguments`. Zwróci ona natomiast nowy `sigman.Wave` o długości wymaganego zakresu czasu który możemy wykorzystać zamieniając ten sam zakres starego `sigman.Wave` metodą `Wave.replace_slice`.

Przykład filtrowania wycinka przebiegu EKG.
```python
import sigman as sm
from sigman import file_manager as fm
from sigman import analyzer
from sigman import visualizer as vis

ecg = fm.import_wave('example_data/EKG.dat', 'ecg')
composite_data = sm.Composite_data(waves={'ecg':ecg})

butterworth = analyzer.import_procedure('modify_filter_butterworth')
arguments = butterworth.default_arguments
arguments['N'] = 3
arguments['Wn'] = 30
filtered_wave = analyzer.modify_wave(composite_data.waves['ecg'], 55, 60, butterworth, arguments)
composite_data.waves['ecg'].replace_slice(55,60, filtered_wave)

vis.visualize_composite_data(composite_data, begin_time=55, end_time=65, 
    title="Porównanie przefiltrowanego fragmentu <55s, 60s> i nieprzefiltrowanego <60s, 65s>")
```

##### Odnajdywanie punktów
Punkty możemy odnaleźć importując procedurę typu `points` i aplikując ją funkcją `analyzer.find_points`. Funkcja ta przymuje jako argumenty `sigman.Composite_data`, który chcemy badać, początek oraz koniec zakresu czasowego, moduł procedury oraz argumenty oparte na `procedure.default_arguments`. Zwróci ona `sigman.Points`, który możemy dodać do reszty danych przez `Composite_data.add_points` lub do innego istniejącego zestawu punktów przez `Points.add_points`.

Przykład odnajdywania punktów DBP na całym przebiegu BP.
```python
import sigman as sm
from sigman import file_manager as fm
from sigman import analyzer
from sigman import visualizer as vis

bp = fm.import_wave('example_data/BP.dat', 'bp')
composite_data = sm.Composite_data(waves={'bp':bp})

dbp_finder = analyzer.import_procedure('points_dbp_simple')
# obliczamy zakres na którym mamy wszystkie dane (przebieg BP)
begin_time, end_time = composite_data.calculate_time_range(['bp'])
dbp = analyzer.find_points(composite_data, begin_time, end_time, dbp_finder, dbp_finder.default_arguments)
composite_data.add_points(dbp, 'dbp')

vis.visualize_composite_data(composite_data)
```
##### Obliczanie parametrów
Parametry możemy obliczyć importując procedurę typu `parameter` i aplikując ją funkcją `analyzer.calculate_parameter`. Funkcja ta przyjmuje `sigman.Composite_data`, listę tuples zawierających początek i koniec zakresów czasowych na których chcemy parametr obliczyć, moduł procedury i dodatkowe argumenty oparte na `procedure.default_arguments`.

Przykład obliczenia częstotliwości bicia serca na zakresach <0s,15s>, <15s,60s> oraz <60s,120s> w oparciu o przebieg EKG.
```python
import sigman as sm
from sigman import file_manager as fm
from sigman import analyzer
from sigman import visualizer as vis

ecg = fm.import_wave('example_data/EKG.dat', 'ecg')
composite_data = sm.Composite_data(waves={'ecg':ecg})

# odnajdujemy punkty R
r_finder = analyzer.import_procedure('points_r_simple')
begin_time, end_time = composite_data.calculate_time_range(['ecg'])
r = analyzer.find_points(composite_data, begin_time, end_time, r_finder, r_finder.default_arguments)
composite_data.add_points(r, 'r')

# obliczamy HR
hr_proc = analyzer.import_procedure('parameter_heart_rate')
param_tuples = [(0,15),(15,60),(60,120)]
hr = analyzer.calculate_parameter(composite_data, param_tuples, hr_proc, hr_proc.default_arguments)
composite_data.add_parameter(hr, 'hr')

vis.visualize_composite_data(composite_data) # Jak na razie wizualizacja parametrów jest niedopracowana
```


Przykłady użycia różnych funkcji biblioteki w pliku `test_sigman.py`.

## Stan obecny
### sigman
Biblioteka nadaje się do wstępnego użytku. Obecnie ważne jest napisanie większej liczby procedur.
- [ ] Wczytywanie danych
  - [x] z plików `.dat`
  - [ ] z signalyzera
- [ ] Zapisywanie danych
  - [x] sygnałów / punktów w plikach `.dat`
  - [x] całych projektów / niedokończonej pracy
  - [ ] obliczonych parametrów w `.xslx` / `.csv`
- [x] Operowanie na danych
  - [x] obróbkę danych na odcinkach czasowych zewnętrznymi procedurami
    - [x] filtracja / modyfikacja sygnału
    - [x] wykrywanie punktów
    - [x] obliczanie średnich parametrów
  - [x] usuwanie i dodawanie pojedynczych punktów
  - [x] przesuwanie przebiegów i punktów względem siebie w czasie
- [x] Wizualizacja danych
  - [x] prosty mechanizm wizualizacji przebiegów, punktów i parametrów

### QtSigman
Aplikacja wymaga pracy nim będzie w stanie użytkowym.
- [ ] Główne okno
  - [ ] wykres danych
    - [x] przebiegi
    - [x] punktowy
    - [x] parametry *do uzgodnienia*
    - [ ] interaktywność
      - [x] skalowanie
      - [x] przesuwanie
      - [x] ukrywanie i pokazywanie elementów
      - [ ] sprawdzanie dokładnych wartości
      - [x] manualna edycja punktów
  - [ ] listy obiektów
    - [x] przebiegi
    - [x] punkty
    - [ ] parametry
    - [x] interaktywność
      - [x] edycja metainformacji
      - [x] tryb edycji punktów
    - [ ] wyświetlanie metainformacji o danych na listach
- [ ] Obsługa plików
  - [x] importowanie przebiegów i punktów
  - [ ] eksportowanie przebiegów i punktów
  - [x] zapisywanie i wczytywanie projektu
- [ ] Obsługa procedur
  - [x] modyfikacja przebiegów
  - [x] odnajdywanie punktów
  - [ ] obliczanie parametrów
  - [ ] przeprowadzanie całościowej analizy (kilka procedur na raz)
  - [ ] wizualizacja wyniku działania procedury przed potwierdzeniem

## Standardy kodu
Kod projektu powinien być utrzymywany jak najbliżej norm [PEP-8](https://www.python.org/dev/peps/pep-0008/). W bibliotece sigman utrzymywane jest nazewnictwo `lowercase_with_underscores`, natomiast w kodzie aplikacji QtSigman w ramach konsystencji z biblioteką PyQt5 wykrozystywane jest nazewnictwo `CamelCase`.

Obecnie dokumentacja jest po polsku i trwają prace nad przetłumaczeniem jej na angielski. Dokumentacja nowo powstałego kodu powinna już być tylko po angielsku.

## Podziękowania
* [Instytut Medycyny Doświadczalnej i Klinicznej im. M. Mossakowskiego PAN](http://imdik.pan.pl/pl/) - wsparcie i nakierowanie projektu, dane
