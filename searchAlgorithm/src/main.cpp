#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <math.h>

#include <iostream>
#include <string>
#include <vector>

#include <bsoncxx/builder/stream/document.hpp>
#include <bsoncxx/json.hpp>

#include <mongocxx/client.hpp>
#include <mongocxx/options/find.hpp>
#include <mongocxx/instance.hpp>
#include <mongocxx/uri.hpp>

#include "../mcr/mcr.h"
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
    std::string sectionId;
    std::string courseId;

    double instructorRating = 0;

    SectionObject(Json::Value thisObject)
    {
      sectionId = thisObject["Meeting_Section"].asString();
      courseId = thisObject["Course"].asString();

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

struct LockedSection {
  std::string courseId;
  std::vector<std::string> sections;
};

std::vector<LockedSection> lockedSections;

bool checkSectionLock(SectionObject *section) {
  bool found = true;

  for (LockedSection course : lockedSections) {
    if (section->courseId == course.courseId) {
      found = false;

      for (std::string sectionId : course.sections) {
        if (section->sectionId == sectionId)
          return true;
      }
    }
  }

  return found;
}

class CourseObject {
  std::string courseCode;

  public:

  std::vector<void*> sections;

  CourseObject(Json::Value thisObject)
  {
    courseCode = thisObject["Course"].asString();

    for (unsigned int place = 0; place < thisObject["Sections"].size(); ++place)
    {
      SectionObject *newSection = new SectionObject(thisObject["Sections"][place]);
      if (checkSectionLock(newSection))
        sections.push_back(newSection);
      else
        delete newSection;
    }
  }
};

int getBlock(int time) {
  int block = (time-800)/100*2;
  int temp = (time-800) - (time-800)/100*100;

  if (temp == 30)
    block++; /* start on this block, so add one */
  else if(temp == 50)
    block++; /* only add one because it ends on this block */

  return block;
}

std::vector<SectionObject> blockedTimes;

bool checkConflict(void *session1, void *session2, int place1, int place2) {
  SectionObject* typedSection1 = (SectionObject*)session1;
  SectionObject* typedSection2 = (SectionObject*)session2;

  //dimensions of day and weeks
  char schedule[5][29];

  for (int j = 0; j < 5; ++j)
    for (int i = 0; i < 29; ++i)
      schedule[j][i] = 0;

  // Add blocks for 1
  for (OfferingObject offering : typedSection1->offerings) {
    for (int place = 0; place < 5; place++) { //for the days
      if (offering.day[place] == 1) {
        int startBlock = getBlock(offering.time_start);
        int endBlock = getBlock(offering.time_end);

        for (int blockTime = startBlock; blockTime <= endBlock; blockTime++)
        {
          if (schedule[place][blockTime] == 1)
            return false;

          schedule[place][blockTime] = 1;

        }
      }
    }
  }
  
  // Add blocks for 2
  for (OfferingObject offering : typedSection2->offerings) {
    for (int place = 0; place < 5; place++) { //for the days
      if (offering.day[place] == 1) {
        int startBlock = getBlock(offering.time_start);
        int endBlock = getBlock(offering.time_end);

        for (int blockTime = startBlock; blockTime <= endBlock; blockTime++)
        {
          if (schedule[place][blockTime] == 1)
            return false;

          schedule[place][blockTime] = 1;

        }
      }
    }
  }

  //for time blocks
  for (unsigned int coursePlace = 0; coursePlace < blockedTimes.size(); coursePlace++)
    for (int place = 0; place < 5; place++) //for the days
      for (unsigned int offeringPlace = 0; offeringPlace < blockedTimes.at(coursePlace).offerings.size(); offeringPlace++) {
        if (blockedTimes.at(coursePlace).offerings.at(offeringPlace).day[place] == 1) //could maybe switch order for speed
        {
          int startBlock = getBlock(blockedTimes.at(coursePlace).offerings.at(offeringPlace).time_start);
          int endBlock = getBlock(blockedTimes.at(coursePlace).offerings.at(offeringPlace).time_end);

          for (int blockTime = startBlock; blockTime <= endBlock; blockTime++)
          {
            if (schedule[place][blockTime] == 1)
              return false;

            schedule[place][blockTime] = 1;
          }
        }
      }

  return true;
}

int comp(int in1, int in2) {
  return in1-in2;
}

int criteria[2];

int scoreTimeBetween(bool schedule[5][29]) {
  float score = 0;
  for (int y = 0; y < 5; ++y) {
    int first = 0;
    int last = 0;
    bool inside = false;

    for (int x = 0; x < 29; ++x) {
      if (schedule[y][x] == 1) {
        if (inside == false) {
          inside = true;
          first = x;
        }
        last = x;
      }
    }

    int totalClass = 0;
    int totalBlank = 0;

    for (int x = first; x < last; ++x) {
      if (schedule[y][x] == 1) {
        totalClass += 1;
      } else {
        totalBlank += 1;
      }
    }

    if (first == 0 && last == 0)
      continue;

    //find out what percentage of time is in class
    float tempCounter = (float)totalClass/((float)totalBlank + (float)totalClass);
    score += tempCounter;
  }

  return score*100/5 - 50;
}

int scoreAverageClassTime(bool schedule[5][29]) {
  float score = 0;

  for (int x = 0; x < 5; ++x) {
    float dayAverage = 0;
    int dayCount = 0;

    for (int y = 0; y < 29; ++y) {
      if (schedule[x][y] == 1) {
        dayAverage += y;
        dayCount++;
      }
    }

    dayAverage /= dayCount;

    score += dayAverage;
  }

  return score/2;
}

int fit(std::vector<std::vector<void*>> *arrs, std::vector<int> currPath, int pathNum) {
  bool schedule[5][29];

  for (int j = 0; j < 5; ++j)
    for (int i = 0; i < 29; ++i)
      schedule[j][i] = 0;

  for (int place = 0; place < currPath.size(); place++) {
    SectionObject* typedSection = (SectionObject*)arrs->at(place).at(currPath.at(place));

    for (OfferingObject offering : typedSection->offerings) {
      for (int place = 0; place < 5; place++) { //for the days
        if (offering.day[place] == 1) {
          int startBlock = getBlock(offering.time_start);
          int endBlock = getBlock(offering.time_end);

          for (int blockTime = startBlock; blockTime <= endBlock; blockTime++)
            schedule[place][blockTime] = 1;
        }
      }
    }
  }

  int score = 0;
  score += scoreTimeBetween(schedule) * criteria[0];
  score += scoreAverageClassTime(schedule) * criteria[1];
  //std::cout << scoreTimeBetween(schedule) << " " << scoreAverageClassTime(schedule) << std::endl;

  return score;
}

using bsoncxx::builder::stream::document;
using bsoncxx::builder::stream::open_document;
using bsoncxx::builder::stream::close_document;
using bsoncxx::builder::stream::open_array;
using bsoncxx::builder::stream::close_array;
using bsoncxx::builder::stream::finalize;

void outputJSON(std::vector<gen_trim_struct*> *captured, std::vector<CourseObject> *courseObjects) {
  std::string temp = "[[";

  for (gen_trim_struct *curr : *captured) {
    for (int pos = 0; pos < curr->top.size(); ++pos) {
      SectionObject *currSection = (SectionObject*)courseObjects->at(pos).sections.at(curr->top[pos]);
      Json::FastWriter fastWriter;
      temp += fastWriter.write(currSection->thisSection);
      temp += ',';
    }
    temp[temp.size()-1] = ' ';
    temp += "],[";
  }

  temp = temp.substr(0, temp.size()-2);
  temp += "]";

  std::cout << temp << std::endl;
}

int main(int argc, char *argv[]) {
  srand (time(NULL));

  mongocxx::instance inst{};
  mongocxx::client conn{mongocxx::uri{}};

  auto db = conn["scheduler"];

  Json::Value root;
  Json::Value root2;
  Json::Value root3;
  Json::Value root4;
  Json::Value root5;

  Json::Reader reader;

  auto cursor = db["userData"].find(document{} << "sessionID" << argv[1] << finalize);
  for (auto&& doc : cursor) {
    std::string tempBSON = bsoncxx::to_json(doc);
    reader.parse(tempBSON, root, false);
  }

  cursor = db["blockedTimes"].find(document{} << "sessionID" << argv[1] << finalize);
  for (auto&& doc : cursor) {
    std::string tempBSON = bsoncxx::to_json(doc);
    reader.parse(tempBSON, root2, false);
  }

  cursor = db["criteria"].find(document{} << "sessionID" << argv[1] << finalize);
  for (auto&& doc : cursor) {
    std::string tempBSON = bsoncxx::to_json(doc);
    reader.parse(tempBSON, root3, false);
  }

  cursor = db["sections"].find(document{} << "sessionID" << argv[1] << finalize);
  for (auto&& doc : cursor) {
    std::string tempBSON = bsoncxx::to_json(doc);
    reader.parse(tempBSON, root5, false);
  }

  if (root5["sections"].size() != 0) {
    for (Json::Value::iterator itr = root5["sections"].begin() ; itr != root5["sections"].end(); itr++ ) {
      std::string courseId = itr.key().asString();

      LockedSection locked;
      locked.courseId = courseId;

      for (auto section : *itr) {
        locked.sections.push_back(section.asString());
      }

      lockedSections.push_back(locked);
    }
  }

  if(root3["data"].size() == 0)
  {
    criteria[0] = 10;
    criteria[1] = 0;
  } else {
    for (int x = 0; x < 2; ++x) {
      criteria[x] = std::stoi((root3["data"][x]).asString());
    }
  }

  if (criteria[0] == 0 && criteria[1] == 0)
    criteria[0] = 10;

  std::vector<Json::Value> objectVector;
  std::vector<CourseObject> courseObjects;

  for (auto&& obj : root["Data"])
  {
    std::string courseCode = obj.asString();
    cursor = db["cachedCourses"].find(document{} << "Course" << courseCode << finalize);

    for (auto&& doc : cursor) {
      std::string tempBSON = bsoncxx::to_json(doc);
  
      reader.parse(tempBSON, root4, false);
      objectVector.push_back(root4["Data"]);
    }
  }

  blockedTimes.push_back(root2);

  /* return if there are no elements */
  if (objectVector.size() == 0)
  {
    std::cout << "null" << std::endl;
    return 0;
  }

  for(unsigned int x = 0; x < objectVector.size(); x++)
    courseObjects.push_back(objectVector[x]);

  std::vector<std::vector<void*>> sectionsGroup;

  for (auto x : courseObjects) {
    sectionsGroup.push_back(x.sections);
  }

  // Run
  std::vector<gen_trim_struct*> captured;
  gen(sectionsGroup, comp, fit, checkConflict, &captured);

  if (captured.size() == 0)
  {
    std::cout << "null" << std::endl;
    return 0;
  }

  outputJSON(&captured, &courseObjects);

  return 0;
 }
