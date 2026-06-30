#include <bits/stdc++.h>
using namespace std;

bool primo(int n){
    if(n < 2) return false;
    for(int i = 2; i * i <= n; i++){
        if(n % i == 0)
            return false;
    }
    return true;
}

int main() {
    int E;
    cin >> E;

    int ans = 0;

    for(int i = 2; i <= E; i++){
        if(primo(i))
            ans++;
    }
    if (ans == 1){
        cout<<"aaa\n";
    }
    else
    cout << ans << '\n';
}