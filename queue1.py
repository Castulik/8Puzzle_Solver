# Queue - FIFO - Fronta


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


class Queue:
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
            raise Exception("Queue is empty!")

        else:
            data = self.head.get_data()

            if self.size > 1:
                next_node = self.head.get_next()
                next_node.set_prev(None)
                self.head = next_node
            else:
                self.head = None
                self.tail = None

            self.size -= 1

            return data

    def print_list(self):
        current = self.head

        while current != None:
            print(current.get_data())
            current = current.get_next()