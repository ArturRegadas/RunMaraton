#include <bits/stdc++.h>
using namespace std;

bool compare(pair<char, double>a, pair<char, double> b){    
    return a.second > b.second;
}

int main(){

    vector<pair<char, double>> nums(3);
    double a, b, c;
    scanf("%lf %lf %lf", &a, &b, &c);
    nums[0] = {'A', a};
    nums[1] = {'B', b};
    nums[2] = {'C', c};
    sort(nums.begin(), nums.end(), compare);

    if(nums[0].second == nums[1].second){
        printf("Empatou\n");
    }
    else{
        printf("Equipe %c ganhou\n", nums[0].first);
    }

    return 0;
}