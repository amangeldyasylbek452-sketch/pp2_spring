#1
import sys
import heapq
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
a = data[1:n + 1]
heapq.heapify(a)
answer = 0
while len(a) > 1:
    x = heapq.heappop(a)
    y = heapq.heappop(a)
    s = x + y
    answer += s
    heapq.heappush(a, s)
print(answer)

#2
import heapq
n = int(input())
a = list(map(int, input().split()))
a = [-x for x in a]
heapq.heapify(a)
while len(a) > 1:
    x = -heapq.heappop(a)
    y = -heapq.heappop(a)
    if x > y:
        heapq.heappush(a, -(x - y))
print(-a[0] if a else 0)

#3
import heapq
n, m = map(int, input().split())
a = list(map(int, input().split()))
a = [-x for x in a]
heapq.heapify(a)
answer = 0
for _ in range(m):
    x = -heapq.heappop(a)
    answer += x
    x -= 1
    if x > 0:
        heapq.heappush(a, -x)
print(answer)

#4
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
k = data[1]
a = data[2:]
a.sort()
b = []
i = 0
j = 0
ans = 0
def get_min():
    global i, j

    if i < n and j < len(b):
        if a[i] <= b[j]:
            x = a[i]
            i += 1
            return x
        else:
            x = b[j]
            j += 1
            return x
    if i < n:
        x = a[i]
        i += 1
        return x
    x = b[j]
    j += 1
    return x
while True:
    x = get_min()
    if x >= k:
        print(ans)
        break
    if i >= n and j >= len(b):
        print(-1)
        break
    y = get_min()
    new_value = x + 2 * y
    b.append(new_value)
    ans += 1
    
#5
import heapq
def prin(a):
    print(a)
def insert(b, c):
    heapq.heappush(b, c)
    if len(b) > y:
        removed = heapq.heappop(b)
        return -removed
    return 0
x, y = map(int, input().split())
d = []
total = 0
w = 0
while x > w:
    z = input().split()
    if z[0] == 'print':
        prin(total)
    elif z[0] == 'insert':
        value = int(z[1])
        removed = insert(d, value)
        total += value
        total += removed
    w += 1