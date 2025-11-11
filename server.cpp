
#include "crow.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<string> splitLines(const string& text) {
    vector<string> lines;
    stringstream ss(text);
    string line;
    while (getline(ss, line)) lines.push_back(line);
    return lines;
}

int main() {
    crow::SimpleApp app;

    CROW_ROUTE(app, "/compare").methods("POST"_method)
    ([](const crow::request& req) {
        auto body = crow::json::load(req.body);
        if (!body) return crow::response(400, "Invalid JSON");

        string userCode = body["user_code"].s();
        string refCode  = body["reference_code"].s();

        auto user = splitLines(userCode);
        auto refc = splitLines(refCode);

        crow::json::wvalue result;
        crow::json::wvalue::list diffs;

        int maxLines = max(user.size(), refc.size());
        for (int i = 0; i < maxLines; i++) {
            if (i >= user.size() || i >= refc.size() || user[i] != refc[i]) {
                crow::json::wvalue diff;
                diff["line"] = i + 1;
                diff["user"] = (i < user.size()) ? user[i] : "";
                diff["ref"]  = (i < refc.size()) ? refc[i] : "";
                diffs.push_back(diff);
            }
        }

        result["differences"] = diffs;
        return crow::response(result);
    });

    app.port(5000).multithreaded().run();
}
