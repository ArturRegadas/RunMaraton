from runSubmissions import RunSubimission

code = r"""
#include <stdio.h>
int main(){
    printf("Equipe C ganhou\n");
    return 0;
}"""

print(RunSubimission(code, "c", "2024IJ", "Artur"))