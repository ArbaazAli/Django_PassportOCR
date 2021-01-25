from django.shortcuts import render, redirect
from .models import SavePassport
from django.http import HttpResponse

import cv2
import pyexcel
from passporteye import read_mrz
import pytesseract
from pytesseract import Output

# pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


states = ['Andhra Pradesh', 'Hyderabad', 'Arunachal Pradesh', 'Itanagar', 'Assam', 'Dispur', 'Bihar', 'Patna',
          'Chhattisgarh', 'Raipur', \
          'Goa', 'Panaji', 'Gujarat', 'Gandhinagar', 'Haryana', 'Chandigarh', 'Himachal Pradesh', 'Shimla', 'Jharkhand',
          'Ranchi', 'Karnataka', \
          'Bangalore', 'Kerala', 'Thiruvananthapuram', 'Madhya Pradesh', 'Bhopal', 'Maharashtra', 'Mumbai', 'Manipur',
          'Imphal', 'Meghalaya', \
          'Shillong', 'Mizoram', 'Aizawl', 'Nagaland', 'Kohima', 'Odisha', 'Bhubaneshwar', 'Punjab', 'Chandigarh',
          'Rajasthan', 'Jaipur', 'Sikkim', \
          'Gangtok', 'Tamil Nadu', 'Chennai', 'Telangana', 'Hyderabad', 'Tripura', 'Agartala', 'Uttarakhand',
          'Dehradun', 'Uttar Pradesh', 'Lucknow', \
          'West Bengal', 'Kolkata', 'Andaman and Nicobar Islands', 'Port Blair', 'Chandigarh', 'Dadra and Nagar Haveli',
          ' Daman & Diu', \
          'The Government of NCT of Delhi', 'Delhi', 'Jammu & Kashmir', 'Srinagar', 'Jammu', 'Ladakh', 'Leh',
          'Lakshadweep', 'Kavaratti', 'Puducherry', 'Puducherry']


def home(request):
    if request.method == 'POST':
        error = 'Error! Image is not clear!'
        image = cv2.imread(f'{request.FILES["passport"]}')
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        custom_config = r'--oem 3 --psm 6'
        details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang='eng')
        places = []

        for i in states:
            for j in details['text']:
                if i.upper() in j:
                    places.append(i)

        if places:
            if len(places) >= 2:
                place_of_birth = ",".join([p for p in places[:-1]])
                place_of_issue = places[-1]
                # print(f'Place of Birth: {",".join([p for p in places[:-1]])}')
                # print(f'Place of Issued: {places[-1]}')
            else:
                error = 'Error! Could not find Place of birth and Place of issue.'
                return render(request, 'home.html', {'error': error})
        else:
            error = 'Error! Image is not clear!'
            return render(request, 'home.html', {'error': error})

        mrz = read_mrz(f'{request.FILES["passport"]}')
        details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang='eng')
        try:
            mrz_data = mrz.to_dict()

        except AttributeError:
            return render(request, 'home.html', {'error': error})

        surname = mrz_data['surname']
        name = mrz_data['names']
        passport_type = mrz_data['type']
        passport_number = mrz_data['number']
        country = mrz_data['country']
        sex = mrz_data['sex']
        date_of_birth = mrz_data['date_of_birth']
        expiry_date = mrz_data['expiration_date']

        with open('passport.txt', 'a+') as f:
            f.write(f'Nationality : {country}\n')
            f.write(f'Surname : {surname}\n')
            f.write(f'Given Name : {name}\n')
            f.write(f'Sex : {sex}\n')
            f.write(f'Passport type : {passport_type[0]}\n')
            f.write(f'Passport Number : {passport_number[:-1]}\n')
            f.write(f'Date of Birth : {date_of_birth[4:]}/{date_of_birth[2:4]}/19{date_of_birth[0:2]}\n')
            f.write(f'Place of Birth: {place_of_birth}\n')
            f.write(f'Place of Issue: {place_of_issue}\n')
            f.write(f'Expiration Date : {expiry_date[4:]}/{expiry_date[2:4]}/20{expiry_date[0:2]}\n')

        data_list = []  # to store dictionary 'dic'
        dic = {}  # store key values from text file

        context = {
            'Nationality': country,
            'Surname': surname or 'Enter Surname',
            'Given_name': name,
            'Sex': sex,
            'Passport_type': passport_type[0],
            'Passport_number': passport_number[:-1],
            'Date_of_Birth': f'{date_of_birth[4:]}/{date_of_birth[2:4]}/19{date_of_birth[0:2]}',
            'Place_of_Birth': place_of_birth,
            'Place_of_Issue': place_of_issue,
            'Expiration_Date': f'{expiry_date[4:]}/{expiry_date[2:4]}/20{expiry_date[0:2]}',
        }

        with open('passport.txt') as f:
            # print (f)
            for line in f:
                # print (line)
                key, value = line.split(":")
                dic[key.strip(" ")] = value.strip(" ")
                if line.startswith("Expiration Date"):
                    print('--Added to dictionary--')
                    data_list.append(dic.copy())
                    continue

        print(context)
        pyexcel.save_as(records=data_list, dest_file_name="passport.xlsx")

        return render(request, 'form.html', context)
        # return redirect('form')
        # return context

    else:
        return render(request, 'home.html')


def form(request):
    if request.method == 'POST':
       
        passport_data = SavePassport(
            given_name=request.POST['given_name'],
            surname=request.POST['surname'],
            date_of_birth=request.POST['date_of_birth'],
            place_of_birth=request.POST['place_of_birth'],
            sex=request.POST['sex'],
            nationality=request.POST['nationality'],
            passport_number=request.POST['passport_number'],
            passport_type=request.POST['passport_type'],
            place_of_issue=request.POST['place_of_issue'],
            expiration_date=request.POST['expiration_date'],
            address=request.POST['address'],
        )

        passport_data.save()
        
        return redirect('home')
            
    return render(request, 'form.html')