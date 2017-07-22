#include <bson.h>
#include <mongoc.h>
#include <iostream>
#include <algorithm>

#include "json.h"

std::string dayArray[] = {"Mon", "Tues", "Wed", "Thur", "Fri"};

class OfferingObject {
    public:
    
    bool day[5] = {0, 0, 0, 0, 0};
    
    int time_start;
    int time_end;
    
    OfferingObject(Json::Value thisObject)
    {
        for(int place = 0; place < 5; ++place)
        {
            if (thisObject["Day"].asString().find(dayArray[place]) != std::string::npos)
                day[place] = 1;
        }
        
        time_start = std::stoi(thisObject["Time_Start"].asString());
        time_end = std::stoi(thisObject["Time_End"].asString());
        
        /*std::cout << "Adding " << thisObject["Day"] << " " << time_start << " to " << time_end << std::endl;
        std::cout << thisObject << std::endl << std::endl;*/
    }
};

class SectionObject {
    public:
    
    std::vector<OfferingObject> offerings;
    Json::Value thisSection;
    
    double instructorRating = 0;
    
    SectionObject(Json::Value thisObject)
    {
        for (unsigned int place = 0; place < thisObject["Offerings"].size(); ++place)
            if (thisObject["Offerings"][place]["Section_Type"] != "EXAM")
                offerings.push_back(thisObject["Offerings"][place]);
        
        thisSection = thisObject;
        
        if (offerings.size() > 0)
        {
            std::string ratingString = thisObject["Instructors_Rating"].asString();
            
            if (ratingString == "")
                instructorRating = 0;
            else
                instructorRating = std::stod(thisObject["Instructors_Rating"].asString());
        }
    }
};

class CourseObject {
    std::string courseCode;
    
    public:
    
    std::vector<SectionObject> sections;
    
    CourseObject(Json::Value thisObject)
    {
        courseCode = thisObject["Course"]["Course"].asString();
        
        for (unsigned int place = 0; place < thisObject["Course"]["Sections"].size(); ++place)
        {
            sections.push_back(thisObject["Course"]["Sections"][place]);
        }
    }
};

int getBlock(int time)
{
    int block = (time-800)/100*2;
    int temp = (time-800) - (time-800)/100*100;
    
    if (temp == 30)
        block++; /* start on this block, so add one */
    else if(temp == 50)
        block++; /* only add one because it ends on this block */
    
    return block;
}

bool checkConflict(std::vector<SectionObject*> checkArray, std::vector<SectionObject> *blockedTimes)
{
    //dimensions of day and weeks
    char schedule[5][29];
    
    for (int j = 0; j < 5; ++j)
        for (int i = 0; i < 29; ++i)
            schedule[j][i] = 0;
    
    //for courses
    for (unsigned int coursePlace = 0; coursePlace < checkArray.size(); coursePlace++)
        for (int place = 0; place < 5; place++) //for the days
            for (unsigned int offeringPlace = 0; offeringPlace < checkArray.at(coursePlace)->offerings.size(); offeringPlace++)
                if (checkArray.at(coursePlace)->offerings.at(offeringPlace).day[place] == 1) //could maybe switch order for speed
                {
                    int startBlock = getBlock(checkArray.at(coursePlace)->offerings.at(offeringPlace).time_start);
                    int endBlock = getBlock(checkArray.at(coursePlace)->offerings.at(offeringPlace).time_end);
                    
                    for (int blockTime = startBlock; blockTime <= endBlock; blockTime++)
                    {
                        if (schedule[place][blockTime] == 1)
                            return 1;
                        
                        schedule[place][blockTime] = 1;
                        
                    }
                }
    
    //for time blocks
    for (unsigned int coursePlace = 0; coursePlace < blockedTimes->size(); coursePlace++)
        for (int place = 0; place < 5; place++) //for the days
            for (unsigned int offeringPlace = 0; offeringPlace < blockedTimes->at(coursePlace).offerings.size(); offeringPlace++)
            {
                if (blockedTimes->at(coursePlace).offerings.at(offeringPlace).day[place] == 1) //could maybe switch order for speed
                {
                    int startBlock = getBlock(blockedTimes->at(coursePlace).offerings.at(offeringPlace).time_start);
                    int endBlock = getBlock(blockedTimes->at(coursePlace).offerings.at(offeringPlace).time_end);

                    for (int blockTime = startBlock; blockTime <= endBlock; blockTime++)
                    {
                        if (schedule[place][blockTime] == 1)
                            return 1;
                        
                        schedule[place][blockTime] = 1;
                    }
                }
            }
    
    
    
    return 0;
}

void generateSchedules(std::vector<CourseObject> *root, unsigned int depth, std::vector<SectionObject*> currentPath, std::vector<SectionObject*> *workingSections, std::vector<SectionObject> *blockedTimes)
{
    unsigned int maxDepth = root->at(depth).sections.size();
    
    std::vector<SectionObject*> tempPath;
    
    for (unsigned int place = 0; place < maxDepth; ++place)
    {
        tempPath = currentPath;
        tempPath.push_back(&(root->at(depth).sections.at(place)));
        
        //make sure there's more than one to compare
        if (!checkConflict(tempPath, blockedTimes))
        {
            if (tempPath.size() < root->size())
                generateSchedules(root, depth+1, tempPath, workingSections, blockedTimes);
            else if (depth == root->size()-1) {
                //outputJSON(root.at(depth).sections.at(place).thisSection);
                
                for (unsigned int w = 0; w < tempPath.size(); w++)
                    workingSections->push_back(tempPath.at(w));
                
                workingSections->push_back(NULL);
            }
        }
    }
    
    return;
}

struct Totals
{
    //for schedule
    double timeBefore = -1;
    double timeAfter = -1;
    double timeTogether = -1;
    double averageClassTime = -1;
    double classLength = -1;
    double teacherRating = -1;
};

struct ToSort
{
    std::vector<SectionObject*> pointer;
    double score;
};

int getTimeBefore(std::vector<SectionObject*> unsorted)
{
    int counter = 0;
    int timeCounter = -1;
    
    for (int day = 0; day < 5; ++day)
    {
        for (int x = 0; x < unsorted.size(); ++x)
            for (int offering = 0; offering < unsorted.at(x)->offerings.size(); ++offering)
                if (unsorted.at(x)->offerings.at(offering).day[day] == 1)
                    if (unsorted.at(x)->offerings.at(offering).time_start < timeCounter || timeCounter == -1)
                        timeCounter = unsorted.at(x)->offerings.at(offering).time_start;
        
        if (timeCounter != -1)
            counter += timeCounter;
        
        timeCounter = -1;
    }
    
    return counter;
}

int getTimeAfter(std::vector<SectionObject*> unsorted)
{
    int counter = 0;
    int timeCounter = -1;
    
    for (int day = 0; day < 5; ++day)
    {
        for (int x = 0; x < unsorted.size(); ++x)
            for (int offering = 0; offering < unsorted.at(x)->offerings.size(); ++offering)
                if (unsorted.at(x)->offerings.at(offering).day[day] == 1)
                
                    if (unsorted.at(x)->offerings.at(offering).time_start > timeCounter || timeCounter == -1)
                        timeCounter = unsorted.at(x)->offerings.at(offering).time_start;
        
        if (timeCounter != -1)
            counter += timeCounter;
        
        timeCounter = -1;
    }
    
    return counter;
}

int getClassLength(std::vector<SectionObject*> unsorted)
{
    int counter = 0;
    //more classes means shorter classes
    //this counts amount of classes
    
    for (int x = 0; x < unsorted.size(); ++x)
        for (int offering = 0; offering < unsorted.at(x)->offerings.size(); ++offering)
            counter++;
    
    return counter;
}

int getAverageClassTime(std::vector<SectionObject*> unsorted)
{
    int counter = 0;
    
    for (int x = 0; x < unsorted.size(); ++x)
        for (int offering = 0; offering < unsorted.at(x)->offerings.size(); ++offering)
        {
            counter += unsorted.at(x)->offerings.at(offering).time_start;
        }
    
    return counter;
}

int getTeacherRatings(std::vector<SectionObject*> unsorted)
{
    double counter = 0;
    
    for (int x = 0; x < unsorted.size(); ++x)
    {
        counter += unsorted.at(x)->instructorRating;
    
        //std::cout << unsorted.at(x)->instructorRating << std::endl;
    }
    
    return counter*100;
}

int getTimeTogether(std::vector<SectionObject*> unsorted)
{
    int counter = 0;
    double tempCounter = 0;
    
    for (int day = 0; day < 5; ++day)
    {
        int schedule[28];
        
        for (int i = 0; i < 28; ++i)
            schedule[i] = 0;
        
        for (int x = 0; x < unsorted.size(); ++x)
            for (int offering = 0; offering < unsorted.at(x)->offerings.size(); ++offering)
            {
                if (unsorted.at(x)->offerings.at(offering).day[day] == 1)
                {
                    int startBlock = getBlock(unsorted.at(x)->offerings.at(offering).time_start);
                    int endBlock = getBlock(unsorted.at(x)->offerings.at(offering).time_end);
                    
                    for (int blockTime = startBlock; blockTime <= endBlock; blockTime++)
                        schedule[blockTime] = 1;
                }
            }
        
        int first = 0;
        int last = 0;
        bool inside = false;
        
        for (int x = 0; x < 28; ++x)
        {
            if (schedule[x] == 1)
            {
                if (inside == false)
                {
                    inside = true;
                    first = x;
                }
                last = x;
            }
        }
        
        int totalClass = 0;
        int totalBlank = 0;
        
        for (int x = first; x < last; ++x)
        {
            if (schedule[x] == 1)
            {
                totalClass += 1;
            } else {
                totalBlank += 1;
            }
        }
        
        if (first == 0 && last == 0)
            continue;
        
        //find out what percentage of time is in class
        tempCounter = (float)totalClass/((float)totalBlank + (float)totalClass);
        tempCounter *= 100;
        //std::cout << tempCounter << std::endl;
        counter += (int)tempCounter;
    }
    
    return counter;
}

//crashes with only one schedule
std::vector<std::vector<SectionObject*>> sortSchedule(std::vector<std::vector<SectionObject*>> unsorted, int criteria[2][6])
{
    // 1: 1 - lots time before; 2: 1 - lots of time after; 3: 0 - classes closer together; 4: average class start time 0 - later start
    // 5: 0 - short classes; 6: 
    int weight[6] = {criteria[1][0], criteria[1][1], criteria[1][2], criteria[1][3], criteria[1][4], criteria[1][5]};
    int direction[6] = {criteria[0][0], criteria[0][1], criteria[0][2], criteria[0][3], criteria[0][4], criteria[0][5]};
    
    Totals max;
    Totals min;
    
    //do totals
    for(unsigned int x = 0; x < unsorted.size(); ++x)
    {
        int timeBefore = getTimeBefore(unsorted.at(x));
        int timeAfter = getTimeAfter(unsorted.at(x));
        int timeTogether = getTimeTogether(unsorted.at(x));
        int averageClassTime = getAverageClassTime(unsorted.at(x));
        int classLength = getClassLength(unsorted.at(x));
        int teacherRating = getTeacherRatings(unsorted.at(x));
        
        if (timeTogether < -100)
            std::cout << timeTogether << std::endl;
        
        if (max.timeBefore < timeBefore || max.timeBefore == -1)
            max.timeBefore = timeBefore;
        if (min.timeBefore > timeBefore || min.timeBefore == -1)
            min.timeBefore = timeBefore;
            
        if (max.timeAfter < timeAfter || max.timeAfter == -1)
            max.timeAfter = timeAfter;
        if (min.timeAfter > timeAfter || min.timeAfter == -1)
            min.timeAfter = timeAfter;
        
        if (max.timeTogether < timeTogether || max.timeTogether == -1)
            max.timeTogether = timeTogether;
        if (min.timeTogether > timeTogether || min.timeTogether == -1)
            min.timeTogether = timeTogether;
            
        if (max.averageClassTime < averageClassTime || max.averageClassTime == -1)
            max.averageClassTime = averageClassTime;
        if (min.averageClassTime > averageClassTime || min.averageClassTime == -1)
            min.averageClassTime = averageClassTime;
        
        if (max.classLength < classLength || max.classLength == -1)
            max.classLength = classLength;
        if (min.classLength > classLength || min.classLength == -1)
            min.classLength = classLength;
        
        if (max.teacherRating < teacherRating || max.teacherRating == -1)
            max.teacherRating = teacherRating;
        if (min.teacherRating > teacherRating || min.teacherRating == -1)
            min.teacherRating = teacherRating;
    }
    
    std::vector<ToSort> sortArray;
    
    for(unsigned int x = 0; x < unsorted.size(); ++x)
    {
        double tempScore = 0;
        double tempValue;
        double tempAverage;
        
        //
        
        tempValue = 0;
        tempAverage = (max.timeBefore + min.timeBefore)/2;
        tempValue = (getTimeBefore(unsorted.at(x)) - tempAverage)/tempAverage*10;
        
        if (direction[0] == 0)
            tempValue = 10 - tempValue;
        tempScore += tempValue*weight[0];
        
        //
        
        tempValue = 0;
        tempAverage = (max.timeAfter + min.timeAfter)/2;
        tempValue = (min.timeAfter - getTimeAfter(unsorted.at(x)))/tempAverage*10;
        
        if (direction[1] == 1)
            tempValue = 10 - tempValue;
        tempScore += tempValue*weight[1];
        
        //
        
        tempValue = 0;
        tempAverage = (max.timeTogether + min.timeTogether)/2;
        tempValue = (getTimeTogether(unsorted.at(x)) - tempAverage)/tempAverage*10;
        
        if (direction[2] == 1)
            tempValue = 10 - tempValue;
        tempScore += tempValue*weight[2];
        
        //
        
        tempValue = 0;
        tempAverage = (max.averageClassTime + min.averageClassTime)/2;
        tempValue = (getAverageClassTime(unsorted.at(x)) - tempAverage)/tempAverage*10;
        
        if (direction[3] == 0)
            tempValue = 10 - tempValue;
        tempScore += tempValue*weight[3];

        //
        
        tempValue = 0;
        tempAverage = (max.classLength + min.classLength)/2;
        tempValue = (getClassLength(unsorted.at(x)) - tempAverage)/tempAverage*10;
        
        if (direction[4] == 0)
            tempValue = 10 - tempValue;
        tempScore += tempValue*weight[4];

        //
        
        tempValue = 0;
        tempAverage = (max.teacherRating + min.teacherRating)/2;
        
        if (tempAverage != 0)
            tempValue = (getTeacherRatings(unsorted.at(x)) - tempAverage)/tempAverage*10;
        
        if (direction[5] == 0)
            tempValue = 10 - tempValue;
        tempScore += tempValue*weight[5];
        
        //
        
        sortArray.push_back(ToSort());
        sortArray.at(sortArray.size()-1).pointer = unsorted.at(x);
        sortArray.at(sortArray.size()-1).score = tempScore;
    }
    
    std::sort(sortArray.begin(), sortArray.end(), 
        [] (const ToSort struct1, const ToSort struct2)
        {
            return (struct1.score > struct2.score);
        }
    );
    
    for(unsigned int x = 0; x < unsorted.size(); ++x)
    {
        unsorted.at(x) = sortArray.at(x).pointer;
    }
    
    //do scores
    //todo: code
    
    return unsorted;
}

std::vector<std::vector<SectionObject*>> mapSchedules(std::vector<SectionObject*> *workingSections, int criteria[2][6])
{
    std::vector<std::vector<SectionObject*>> sorted;
    std::vector<SectionObject*> current;
    
    for (unsigned int x = 0; x < workingSections->size() - 1; ++x)
    {
        if (workingSections->at(x) != NULL)
        {
            current.push_back(workingSections->at(x));
        } else {
            sorted.push_back(current);
            current.clear();
        }
    }
    
    sorted.push_back(current);
    
    return sortSchedule(sorted, criteria);
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
    
    mongoc_init ();
    
    client = mongoc_client_new ("mongodb://localhost:27017/");
    
    collection = mongoc_client_get_collection (client, "scheduler", "userData");
    query = bson_new ();
    
    BSON_APPEND_UTF8 (query, "sessionID", argv[1]);
    cursor = mongoc_collection_find(collection, MONGOC_QUERY_NONE, 0, 0, 0, query, NULL, NULL);
    
    while (mongoc_cursor_next (cursor, &doc)) {
        str = bson_as_json (doc, NULL);
        bool parsedSuccess = reader.parse(str, root, false);
        bson_free (str);
    }
    
    collection = mongoc_client_get_collection (client, "scheduler", "blockedTimes");
    query = bson_new ();
    BSON_APPEND_UTF8 (query, "sessionID", argv[1]);
    cursor = mongoc_collection_find(collection, MONGOC_QUERY_NONE, 0, 0, 0, query, NULL, NULL);
    
    Json::Value root2;
    
    while (mongoc_cursor_next (cursor, &doc)) {
        str = bson_as_json (doc, NULL);
        bool parsedSuccess = reader.parse(str, root2, false);
        bson_free (str);
    }
    
    collection = mongoc_client_get_collection (client, "scheduler", "criteria");
    query = bson_new ();
    BSON_APPEND_UTF8 (query, "sessionID", argv[1]);
    cursor = mongoc_collection_find(collection, MONGOC_QUERY_NONE, 0, 0, 0, query, NULL, NULL);
    
    Json::Value root3;
    
    while (mongoc_cursor_next (cursor, &doc)) {
        str = bson_as_json (doc, NULL);
        bool parsedSuccess = reader.parse(str, root3, false);
        bson_free (str);
    }
    
    int criteria[2][6];
    
    if(root3.size() == 0)
    {
        for (int x = 0; x < 6; ++x) {
            criteria[0][x] = 0;
            criteria[1][x] = 0;
        }
    } else {
        for (int x = 0; x < 6; ++x) {
            criteria[0][x] = std::stoi((root3["Direction"][x]).asString());
            criteria[1][x] = std::stoi((root3["Weight"][x]).asString());
        }
    }
    
    std::vector<Json::Value> objectVector;
    std::vector<SectionObject> blockedTimes;
    
    /* sort list based on sizes for speed increase */
    for(unsigned int x = 0; x < root["Data"].size(); x++)
    {
        objectVector.push_back(root["Data"][x]);
    }
    
    /* sort list based on sizes for speed increase */
    blockedTimes.push_back(root2);
    
    //std::cout << root2 << std::endl;
    
    /* return if there are no elements */
    if (objectVector.size() == 0)
    {
        std::cout << "null" << std::endl;
        return 0;
    }
    
    /* sort for minor speed increase */
    std::sort(objectVector.begin(), objectVector.end(), 
        [] (const Json::Value struct1, const Json::Value struct2)
        {
            return (struct1["Course"]["Sections"].size() < struct2["Course"]["Sections"].size());
        }
    );
    
    std::vector<CourseObject> courseObjects;
    std::vector<SectionObject*> empty;
    std::vector<SectionObject*> workingSections;
    
    for(unsigned int x = 0; x < root["Data"].size(); x++)
        courseObjects.push_back(objectVector[x]);
    
    generateSchedules(&courseObjects, 0, empty, &workingSections, &blockedTimes);
    
    /* NULL in workingSections represents split between schedules */
    if (workingSections.size() == 0)
    {
        std::cout << "null" << std::endl;
        return 0;
    }
    
    int start = std::stoi(argv[2]);
    int amount = std::stoi(argv[3]);
    int counter = 0;
    int totalSchedules = 0;
    
    std::string temp = "";
    std::vector<std::vector<SectionObject*>> sortedSchedules = mapSchedules(&workingSections, criteria);
    
    temp += "[[";
    
    //maximum 40 schedules output
    for (unsigned int x = start; x < amount && x < sortedSchedules.size() && x < start + 40; ++x)
    {
        for (unsigned int y = 0; y < sortedSchedules.at(x).size(); ++y)
        {
            Json::FastWriter fastWriter;
            temp += fastWriter.write(sortedSchedules.at(x).at(y)->thisSection);
            temp += ',';
        }
        
        temp[temp.size()-1] = ' ';
        temp += "],[";
    }
    
    temp = temp.substr(0, temp.size()-2);
    
    temp += ",";
    temp += std::to_string(sortedSchedules.size());
    temp += "]";
    
    std::cout << temp << std::endl;
    
    bson_destroy (query);
    mongoc_cursor_destroy (cursor);
    mongoc_collection_destroy (collection);
    mongoc_client_destroy (client);
    mongoc_cleanup ();
    
    return 0;
}
