import chardet

with open(r"C:\Users\ygtyi\Desktop\Code\emailer\işletmeler.txt", "r", encoding="utf-8", errors="replace") as file:
    lines = file.readlines()


numbers = ["0","1","2","3","4","5","6","7","8","9"]
repeating_places =[]
sorted_places =[]
renewed_counter = 1
renewed_place = ""
place_name=""
place_website = ""
isRepeating=False
blacklisted_names=["Symposium","Hard Rock","Wild Bean","Loaded Cafe","Hog's Breath","Cactus Club","Bäckerei","Crawfish Cafe"]

for line in lines:                                       #looks to see if there are repeating place names                                      

    if "Name:" not in line:                              #skips white spaces
        continue
    isRepeating=False
    j=12
    while (j<len(line)-1):
        if(line[j] in numbers or line[j]==","):          #looks to see where the place name ends (because some places have address in their names)
            break                  
        j+=1

    place_name = line[line.find("Name:")+6:j]            #isolates place name
    renewed_place = "[" + str(renewed_counter) + "] Name: " + place_name + ", " + line[line.find("E-mail:"):len(line)-1]
    renewed_counter+=1
    


    if any(word in place_name for word in blacklisted_names):
        isRepeating = True
    else:
        for place in repeating_places:                   #if the place's name is in the blacklist, marks it as repeating
            if place_name in place:
                isRepeating=True
                break   
    

    if isRepeating:                                      #if the place is repeating, skips in the loop
        renewed_counter-=1
        continue 
    else:
        for m in sorted_places:                          #if it's not in the blaclist, looks to see if the place appears in the sorted list
            if(place_name in m):
                isRepeating=True                         #if it is, marks is as repeating
                break
        if isRepeating:
            repeating_places.append(renewed_place)       #repeating place is placed in the blacklist
            renewed_counter-=1
            isRepeating=False
        else:
            sorted_places.append(renewed_place)          #if it doesn't, it is placed in the sorted list

    
    
            
            
with open(r"C:\Users\ygtyi\Desktop\Code\işletmeler_sorted.txt", "w", encoding="utf-8", errors="replace") as file:
    for place in sorted_places:
        file.write(place + "\n")


print("--------------")
for place in repeating_places:
    print(place)






