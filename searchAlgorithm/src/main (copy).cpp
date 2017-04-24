#include <bson.h>
#include <mongoc.h>
#include <iostream>
#include "json.h"

std::string dayArray[] = {"Mon", "Tues", "Wed", "Thur", "Fri"};

int getBlock(int time)
{
    int block = (time-800)/100*2;
    int temp = (time-800) - (time-800)/100*100;
    
    if (temp == 30)
        block++;
    else if(temp == 50)
        block += 2;
    
    return block;
}

bool checkConflict(Json::Value courseArray)
{
    //dimensions of day and weeks
    bool schedule[5][28];
    
    for (int j = 0; j < 5; ++j)
        for (int i = 0; i < 28; ++i)
            schedule[j][i] = 0;
    
    for (int coursePlace = 0; coursePlace < courseArray.size(); coursePlace++)
    {
        for (int place = 0; place < 5; place++)
        {
            for (int offeringPlace = 0; offeringPlace < courseArray[coursePlace]["Offerings"].size(); offeringPlace++)
                if (courseArray[coursePlace]["Offerings"][offeringPlace]["Day"].asString().find(dayArray[place]) != std::string::npos && courseArray[coursePlace]["Offerings"][offeringPlace]["Section_Type"] != "EXAM")
                {
                    int startBlock = getBlock(std::stoi(courseArray[coursePlace]["Offerings"][offeringPlace]["Time_Start"].asString()));
                    int endBlock = getBlock(std::stoi(courseArray[coursePlace]["Offerings"][offeringPlace]["Time_End"].asString()));
                    
                    //std::cout << place << " | " << startBlock << " -> " << endBlock << std::endl;
                    
                    for (int blockTime = startBlock; blockTime <= endBlock; blockTime++)
                    {
                        if (schedule[place][blockTime] == 1)
                            return true;
                        
                        schedule[place][blockTime] = 1;
                    }
                }
        }
    }
    
    return false;
}

void generateSchedules(Json::Value root, Json::Value *addTo)
{
    std::vector<int> finalPlaces;
    std::vector<int> currentPlaces;
    
    std::vector<int> knownConflicts1;
    std::vector<int> knownConflicts2;
    
    Json::Value tempArray;
    
    for (auto itr : root) {
        finalPlaces.push_back(itr["Course"]["Sections"].size());
        currentPlaces.push_back(0);
        
        std::cout << itr["Course"]["Sections"].size() << "\n_____________________________" << std::endl;
    }
    
    while (true)
    {
        tempArray.clear();
        
        for (int place = 0; place < finalPlaces.size(); place++)
        {
            if (currentPlaces[place] >= finalPlaces[place])
            {
                if (place == finalPlaces.size()-1)
                    return;
                
                currentPlaces[place] = 0;
                currentPlaces[place+1]++;
            }
            
            tempArray.append(root[place]["Course"]["Sections"][currentPlaces[place]]);
            
        }
        
        if (!checkConflict(tempArray))
        {
            addTo->append(tempArray);
        }
        
        //std::cout << counter << std::endl;
        //11212
        
        currentPlaces[0]++;
    }
}

int main (int argc, char *argv[])
{
    
    mongoc_client_t *client;
    mongoc_collection_t *collection;
    mongoc_cursor_t *cursor;
    const bson_t *doc;
    bson_t *query;
    char *str;
    
    Json::Value root;
	Json::Reader reader;
    Json::Value toReturn;
    
    mongoc_init ();
    
    client = mongoc_client_new ("mongodb://localhost:27017/");
    collection = mongoc_client_get_collection (client, "scheduler", "userData");
    query = bson_new ();
    BSON_APPEND_UTF8 (query, "sessionID", "77P7H9662F");
    
    cursor = mongoc_collection_find (collection, MONGOC_QUERY_NONE, 0, 0, 0, query, NULL, NULL);
    
    while (mongoc_cursor_next (cursor, &doc)) {
        str = bson_as_json (doc, NULL);
        //printf ("%s\n", str);
        
        bool parsedSuccess = reader.parse(str, root, false);
        
        bson_free (str);
    }
    
    generateSchedules(root["Data"], &toReturn);
    
    //std::cout << toReturn << std::endl;
    std::cout << toReturn.size() << std::endl;
    /*std::cout << "[";
    for (int x = 0; x < toReturn.size(); ++x)
    {
        std::cout << toReturn[x];
        if (x < toReturn.size()-1)
            std::cout << ",\n";
        else
            std::cout << std::endl;
    }
    std::cout << "]\n";*/
    
    bson_destroy (query);
    mongoc_cursor_destroy (cursor);
    mongoc_collection_destroy (collection);
    mongoc_client_destroy (client);
    mongoc_cleanup ();
    
    return 0;
}
