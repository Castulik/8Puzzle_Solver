# Stack - LIFO - Zasobnik


class Node:
    def __init__(self, data):
        self.__next = None
        self.__prev = None
        self.__data = data

    def get_data(self):
        return self.__data

    def set_next(self, nextt):
        self.__next = nextt

    def set_prev(self, prev):
        self.__prev = prev

    def get_next(self):
        return self.__next

    def get_prev(self):
        return self.__prev


class Stack:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        if self.head == None:
            return True
        else:
            return False

    def get_size(self):
        return self.size

    def push(self, data):
        temp = Node(data)

        if self.is_empty():
            self.head = temp
            self.tail = temp
        else:
            self.tail.set_next(temp)
            temp.set_prev(self.tail)
            self.tail = temp

        self.size += 1

    def pop(self):

        if self.is_empty():
            raise Exception("Stack is empty!")
        else:
            data = self.tail.get_data()

            if self.size > 1:
                prev = self.tail.get_prev()
                prev.set_next(None)
                self.tail = prev
            else:
                self.tail = None
                self.head = None

            self.size -= 1
            return data

    def peek(self):
        if not self.is_empty():
            return self.tail.get_data()
        else:
            raise Exception("Stack is empty!")

    def print_list(self):
        current = self.head

        while current != None:
            print(current.get_data())
            current = current.get_next()