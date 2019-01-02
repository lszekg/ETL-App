import datetime
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from openpyxl import Workbook
from .models import Products

from static.etlapp import ScrapperRedux1

def index(request):
    products_list = Products.objects.order_by('-pub_date')
    widths_list = ScrapperRedux1.get_tire_widths()
    # template = loader.get_template('etlapp/index.html')
    context = {
        'products_list': products_list,
        'widths_list': widths_list,
    }
    # return HttpResponse(template.render(context, request))
    return render(request, 'etlapp/index.html', context)

def save_file(request):
    if request.method == "POST":
        data = {}
        if request.POST['selected_product'] == ".TXT":
            product_id = Products.objects.get(id=request.POST['product_id'])
            generate_txt(product_id, 'static/etlapp/files_from_database/product.txt')
        else:
            generate_csv(Products.objects.all(), 'static/etlapp/files_from_database/oponeo.csv')
            return JsonResponse(data)

    return render(request, 'etlapp/index.html')

def generate_csv(Products, file_path):
    wb = Workbook()
    ws = wb.active
    row_count = 1

    ws['A' + str(row_count)] = "ID BD"
    ws['B' + str(row_count)] = "ID Oponeo"
    ws['C' + str(row_count)] = "Producent"
    ws['D' + str(row_count)] = "Nazwa"
    ws['E' + str(row_count)] = "Cena"
    ws['F' + str(row_count)] = "Typ pojazdu"
    ws['G' + str(row_count)] = "Sezon"
    ws['H' + str(row_count)] = "Rozmiar"
    ws['I' + str(row_count)] = "Homologacja"
    ws['J' + str(row_count)] = "Indeks prędkości"
    ws['K' + str(row_count)] = "Indeks nośności"
    ws['L' + str(row_count)] = "Etykieta UE"
    ws['M' + str(row_count)] = "Rok produkcji"
    ws['N' + str(row_count)] = "Kraj produkcji"
    ws['O' + str(row_count)] = "Gwarancja"
    ws['P' + str(row_count)] = "Inne"
    ws['Q' + str(row_count)] = "Data publikacji w bazie"
    row_count += 1

    for product in Products:
        ws['A' + str(row_count)] = product.id
        ws['B' + str(row_count)] = product.ProductID
        ws['C' + str(row_count)] = product.Manufacturer
        ws['D' + str(row_count)] = product.Name
        ws['E' + str(row_count)] = product.Price
        ws['F' + str(row_count)] = product.Car_type
        ws['G' + str(row_count)] = product.season
        ws['H' + str(row_count)] = product.size
        ws['I' + str(row_count)] = product.approval
        ws['J' + str(row_count)] = product.speed_index
        ws['K' + str(row_count)] = product.weight_index
        ws['L' + str(row_count)] = product.sound_index
        ws['M' + str(row_count)] = product.production_year
        ws['N' + str(row_count)] = product.country_of_origin
        ws['O' + str(row_count)] = product.guaranty
        ws['P' + str(row_count)] = product.other_info
        ws['Q' + str(row_count)] = product.pub_date
        row_count += 1

    wb.save(file_path)

def generate_txt(product, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("Produkt: " + product.Name + '\n\n')
        file.write("Id bazy danych: " + str(product.id) + "\n")
        file.write("Id OPONEO: " + str(product.ProductID) + "\n")
        file.write("Producent: " + product.Manufacturer + "\n")
        file.write("Cena: " + product.Price + "\n")
        file.write("Typ pojazdu: " + product.Car_type + "\n")
        file.write("Sezon: " + product.season + "\n")
        file.write("Rozmiar: " + product.size + "\n")
        file.write("Homologacja: " + product.approval + "\n")
        file.write("Indeks prędkości: " + product.speed_index + "\n")
        file.write("Indeks nośności: " + product.weight_index + "\n")
        file.write("Etykieta UE: " + product.sound_index + "\n")
        file.write("Rok produkcji: " + product.production_year + "\n")
        file.write("Kraj produkcji: " + product.country_of_origin + "\n")
        file.write("Gwarancja: " + product.guaranty + "\n")
        file.write("Inne: " + product.other_info + "\n")
        file.write("Data publikacji w bazie: " + str(product.pub_date) + "\n")

def clear_database(request):
    if request.method == "POST":
        summary = "Baza danych została wyczyszczona. Usunięto " + str(len(Products.objects.all())) + " rekordów.\n"
        Products.objects.all().delete()

        data = {
            summary:summary,
        }

        return JsonResponse(data)

    return render(request, 'etlapp/index.html')

def refresh_table(request):
    #increment = int(request.GET['append_increment'])
    #increment_to = increment + 10
    products_list = Products.objects.all().order_by('-pub_date')
    return render(request, 'etlapp/refresh_table.html', {'products_list': products_list})

tires = list()
data_list = list()
date = str(datetime.datetime.now())
def dummy(request):
    global data_list
    global tires
    if request.method == "POST":
        data = {}
        summary = ""

        if request.POST['button_text'] == "ETL":
            width = request.POST['dropdown_id']
            time = ScrapperRedux1.extract(tires, width)
            summary += "Ekstrakcja zakończona. Sparsowano " + str(len(tires)) + "rekordów. Operacja zajęła " + str(int(time/60)) + " min " + str(int(time%60)) + " sekund.\n"
            data_list = ScrapperRedux1.transform(tires)
            summary += "Transformacja zakończona. Przygotowano " + str(len(data_list[0])) + " obiektów. Operacja zajęła " + str(int(data_list[1]/60)) + " min " + str(int(data_list[1]%60)) + " sekund.\n"
            time = ScrapperRedux1.load(data_list[0], date)
            summary += "Ładowanie zakończone. Operacja zajęła " + str(int(time/60)) + " min " + str(int(time%60)) + " sekund.\n"
            data = {
               summary:summary,
            }

        elif request.POST['button_text'] == "EXTRACT":
            tire_widths = ScrapperRedux1.get_tire_widths()
            width = request.POST['dropdown_id']
            extract_time = ScrapperRedux1.extract(tires, width)
            summary += "Ekstrakcja zakończona. Sparsowano " + str(len(tires)) + "rekordów. Operacja zajęła " + str(int(extract_time/60)) + " min " + str(int(extract_time%60)) + " sekund.\n"
            data = {
                summary:summary,
            }

        elif request.POST['button_text'] == "TRANSFORM":
            data_list = ScrapperRedux1.transform(tires)
            summary += "Transformacja zakończona. Przygotowano " + str(len(data_list[0])) + " obiektów. Operacja zajęła " + str(int(data_list[1]/60)) + " min " + str(int(data_list[1]%60)) + " sekund.\n"
            data = {
                summary:summary,
            }

        else:
            time = ScrapperRedux1.load(data_list[0], date)
            summary += "Ładowanie zakończone. Operacja zajęła " + str(int(time/60)) + " min " + str(int(time%60)) + " sekund.\n"
            data = {
                summary:summary,
            }

        return JsonResponse(data)

    return render(request, 'etlapp/index.html')