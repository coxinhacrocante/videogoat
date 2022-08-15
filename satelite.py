import time
import sheets
import gerador_link

print('Satélite Lançado')
while True:
    try:
        online = False
        SH = sheets.Sheets()
        status = SH.receber('Status Servidor!A1:C3')

        data = time.localtime()
        data_str = int(str(data.tm_year)+str(data.tm_mon)+str(data.tm_hour))
        data_min = int(data.tm_min)

        with open('DADOS.txt', 'r') as ar:
            script_txt = ar.readlines()
            data_script = int(script_txt[0])
            data_script_min = int(script_txt[1])
            if data_str == data_script and data_min >= data_script_min and data_script_min +3 >= data_min:
                status[1][0] = "ONLINE"
                online = True
                print('Atualizando Status para Online')
            else: 
                status[1][0] = "OFFLINE"
                print('Atualizando Status para Offline')

            print(data_str)
            print(data_script)
            print(data_min)
            print(data_script_min)
        
        SH.postar('Status Servidor!A1:C3', status)

    except Exception as e:
        print('erro no satelite:'+str(e))


    if online == True:
        time.sleep(1200)
    time.sleep(60)
