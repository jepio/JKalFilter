#include <stdio.h>
#include <stdlib.h>

int* gen_array(int size)
{
    int *array = (int *) malloc(size * sizeof(int));
    if (!array)
        exit(1);
    int i;
    srand(0);

    for (i = 0; i < size; i++)
    {
        array[i] = rand() % size;
    }
    return array;
}

int average(int arr[], int size)
{
    int i;
    long sum = 0;
    for (i = 0; i< size; i++)
    {
        sum += arr[i];
    }
    sum /= size;
    return (int) sum;
}

int main(void){
    printf("test\n");
    return 0;
}
