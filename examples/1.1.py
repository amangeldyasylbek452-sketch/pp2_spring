a = int(input())
b = list(map(str, input().split()))
for i in range(a):
    print(f"{i}:{b[i]}" , end=" ")