"""AVL Tree

Program written for PAMSI by Kornel Stefańczyk nr 235420
5.03.2018
"""

__version__ = '0.60'


def debug(msg, active_debbuging = True):
    """Function print msg in console'
    
    It is using to inform user about tasks of program"""
    if active_debbuging:
        print(msg)


class Node():
    """Basic class for implementing binary trees """
    def __init__(self,key=None, parent=None, rightChild=None, leftChild=None):
        """Class initialisation  """
        self.key=key
        self.parent = parent
        self.rightChild = rightChild 
        self.leftChild = leftChild


class AVLNode(Node):
    """Class contain structure of AVL tree"""
    def __init__(self, key=None, parent=None, rightChild=None, leftChild=None, balance=0):
        Node.__init__(self, key, parent, rightChild, leftChild)
        self.balance = balance






def bst_count(top):
    """Counting number of nodes"""
    if top is None:
        return 0
    return bst_count(top.leftChild) + 1 + bst_count(top.rightChild) 

def bst_height(top):
    """Function return height of children nodes of "top" node """
    if top is None:
        return -1
    left = bst_height(top.leftChild)
    right = bst_height(top.rightChild)
    return 1 + max(left, right)

def bst_find_min(top):
    """Function return node of least element of tree"""
    if top is None:
        raise ValueError("empty tree")
    while top.leftChild:
        top = top.leftChild
    return top

def bst_find_max(top):
    """Function return node of maximum element of tree"""
    if top is None:
        raise ValueError("empty tree")
    while top.rightChild:
        top = top.rightChild
    return top

def bst_insert(root, new_node):
    """Function insert node to tree 
    
    It return root and new created node"""
    parent = None
    node = root
    #Moving through tree to get access to last element of tree
    while node:
        parent = node
        if new_node.key < node.key:
            node = node.leftChild
        else:
            node = node.rightChild
    #If tree is not empty add node on the ond of this tree
    if parent:
        if new_node.key < parent.key:
            parent.leftChild = new_node
            debug("Added new element to tree, key= "+str(new_node.key)+" left child")
        else:
            parent.rightChild = new_node
            debug("Added new element to tree, key= "+str(new_node.key)+" right child")
    else:
        root = new_node
    new_node.parent = parent
    new_node.leftChild = None
    new_node.rightChild = None

    return root, new_node

def bst_transplant(root, node_to_replace, transplanted_node):
    """Function transplant place node from third argument in place of node from second argument

    It return root and transplanted_node"""
    if node_to_replace.parent is None:
        root = transplanted_node
        if root:
            root.parent = None
        return root, transplanted_node
    elif node_to_replace == node_to_replace.parent.leftChild:
        node_to_replace.parent.leftChild = transplanted_node
    else:
        node_to_replace.parent.rightChild = transplanted_node
    if transplanted_node:
        transplanted_node.parent = node_to_replace.parent
    return root, transplanted_node

def bst_delete(root, node):
    """ Function delete node called in as argument

    It return root and node that will be in place of deleted node"""
    debug("Deleting node of tree, key= "+str(node.key))
    if root is None or node is None:
        return root, None
    if node.leftChild is None:
        return bst_transplant(root, node, node.rightChild)
    elif node.rightChild is None:
        return bst_transplant(root, node, node.leftChild)
    else:      #it has left and right child
        y = bst_find_min(node.rightChild)
        if y.parent != node:
            root, _ = bst_transplant(root, y, y.rightChild)
            y.rightChild = node.rightChild
            if y.rightChild:
                y.rightChild.parent = y
        root, _ = bst_transplant(root, node, y)
        y.leftChild = node.leftChild
        y.leftChild.parent = y
        return root, y

def bst_find_successor(root, node):
    """Function return successor of node """
    if root is None or node is None:
        return None
    if node.rightChild:
        return bst_find_min(node.rightChild) #there is no right subtree
    successor = node.parent
    while successor and node == successor.rightChild:
        node = successor
        successor = successor.parent
    return successor

def bst_rotate_left(root, top):
    """Function do left rotation of subtree"""
    if top.rightChild is None:
        debug("There is no right rotation")
        return root, top     #there is no rotation
    node = top.rightChild
    top.rightChild = node.leftChild
    if node.leftChild:
        node.leftChild.parent = top
    node.parent = top.parent
    if top.parent is None:
        root = node # node was root
    elif top == top.parent.leftChild:
        top.parent.leftChild = node
    else:
        top.parent.rightChild = node
    
    node.leftChild = top
    top.parent = node
    debug("Rotated left node with key: "+str(top.key)+" new node instead: "+str(node.key)) 
    return root, node

def bst_rotate_right(root, top):
    """Function do right rotation of subtree"""
    if top.leftChild is None:
        debug("There is no right rotation")
        return root, top
    node = top.leftChild
    top.leftChild = node.rightChild
    if node.rightChild:
        node.rightChild.parent = top
    node.parent = top.parent
    if top.parent is None:
        root = node
    elif top == top.parent.rightChild:
        top.parent.rightChild = node
    else:
        top.parent.leftChild = node
    node.rightChild = top
    top.parent = node 
    debug("Rotated right node with key: "+str(top.key)+" new node instead: "+str(node.key))
    return root, node



def return_tree_inorder(top):
    """Function return tree like a list: left_child, current_node, right_child"""
    if top is None:
        return []
    order = []
    order.extend(return_tree_inorder(top.leftChild))
    order.append(top.key)
    order.extend(return_tree_inorder(top.rightChild))
    return order

def return_tree_preorder(top):
    """Function return tree like a list: current_node, left_child, right_child"""
    if top is None:
        return []
    order = []
    order.append(top.key)
    order.extend(return_tree_inorder(top.leftChild))
    order.extend(return_tree_inorder(top.rightChild))
    return order

def return_tree_postorder(top):
    """Function return tree like a list: left_child, right_child, current_node"""
    if top is None:
        return []
    order = []
    order.extend(return_tree_inorder(top.leftChild))
    order.extend(return_tree_inorder(top.rightChild))
    order.append(top.key)
    return order



def return_avl_tree_inorder(top, interface_type=1):
    """Function print tree like in terminal with balance ratio: left_child, current_node, right_child"""
    if top is None:
        print("empty tree")
    else:
        if top.leftChild is not None:
            return_avl_tree_inorder(top.leftChild)

        if interface_type == 0:
            print(str(top.key)+'('+str(top.balance)+') ', sep=' ', end='', flush=True)
        elif interface_type == 1:
            print(str(top.key)+'('+str(top.balance)+')['+str(bst_height(top))+'] ', sep=' ', end='', flush=True)

        if top.rightChild is not None:
            return_avl_tree_inorder(top.rightChild)

def return_avl_tree_preorder(top, interface_type=1):
    """Function print tree like in terminal with balance ratio: current_node, left_child, right_child"""
    if top is None:
        print("empty tree")
    else:
        if interface_type == 0:
            print(str(top.key)+'('+str(top.balance)+') ', sep=' ', end='', flush=True)
        elif interface_type == 1:
            print(str(top.key)+'('+str(top.balance)+')['+str(bst_height(top))+'] ', sep=' ', end='', flush=True)

        if top.leftChild is not None:
            return_avl_tree_preorder(top.leftChild)
        if top.rightChild is not None:
            return_avl_tree_preorder(top.rightChild)

def return_avl_tree_postorder(top, interface_type=1):
    """Function print tree like in terminal with balance ratio: left_child, right_child, current_node"""
    if top is None:
        print("empty tree")
    else:
        if top.leftChild is not None:
            return_avl_tree_postorder(top.leftChild)

        if interface_type == 0:
            print(str(top.key)+'('+str(top.balance)+') ', sep=' ', end='', flush=True)
        elif interface_type == 1:
            print(str(top.key)+'('+str(top.balance)+')['+str(bst_height(top))+'] ', sep=' ', end='', flush=True)

        if top is not None:
            print(str(top.key)+'('+str(top.balance)+') ', sep=' ', end='', flush=True)



def avl_tree_rebalance(root, y):
    """This function rebalance AVL Tree, and it is using in function like avl_node_insert or avl_node_delete"""
    w = None
    if y.balance == -2:
        x = y.leftChild
        w = x.rightChild
        if x.balance == -1:
            w = x
            x.balance = 0
            y.balance = 0
            root, _ = bst_rotate_right(root, y)
        else:
            w = x.rightChild
            root, _ = bst_rotate_left(root, x)
            root, _ = bst_rotate_right(root, y)
            if w.balance == -1:
                x.balance = 0
                y.balance = 1 #+1
            elif w.balance == 0:
                x.balance = 0
                y.balance = 0
            else: #w.balance == 1
                x.balance = -1
                y.balance = 0
            w.balance = 0
    elif y.balance == 2:
        x = y.rightChild
        w = y.leftChild
        if x.balance == 1:
            w = x
            x.balance = 0
            y.balance = 0
            root, _ = bst_rotate_left(root, y)
        else:
            w = x.leftChild
            root, _ = bst_rotate_right(root, x)
            root, _ = bst_rotate_left(root, y)
            if w.balance == -1:                                
                x.balance = 0
                y.balance = -1
            elif w.balance == 0:
                x.balance = 0
                y.balance = 0
            else:
                x.balance = 1
                y.balance = 0
            w.balance = 0
    return root

def avl_update(node, y):
    """Function update balance parametr of node"""
    while node != y:
        parent = node.parent
        if parent.leftChild == node:
            parent.balance -= 1
        else:
            parent.balance += 1
        node = parent

def avl_node_insert(root, new_node):
    """Function insert node to tree and update it and balance to maintain avl type of tree"""
    root, _ = bst_insert(root, new_node)
    y = new_node
    while y != root:
        y = y.parent
        if y.balance != 0:
            break
    avl_update(new_node, y)
    root = avl_tree_rebalance(root, y)
    return root, new_node

def avl_node_delete(root, node):
    """Function delete node to tree and update it and balance to maintain avl type of tree"""
    if node is None:
        return node
    u = bst_find_successor(root,node)
    root, _ = bst_delete(root, node)
    succ = bst_find_successor(root,node) 
    if succ:
        succ.balance = bst_height(succ.rightChild) - bst_height(succ.leftChild)
    q = node.parent
    if u:
        u.balance = bst_height(u.rightChild) - bst_height(u.leftChild)
        if q is None:
            q = u
    while q:
        q.balance = bst_height(q.rightChild) - bst_height(q.leftChild)
        root = avl_tree_rebalance(root, q)
        q = q.parent
    if u:
        return root, u
    return root, None


def print_status_of_tree(root, type_of_moving='in'):
    """Function print in console information about tree. 
    
    It print height of tree, number of nodes in tree and structure of tree.
    type_of_moving='in'   - print structure of tree inorder 
                   'pre'  - print structure of tree preorder
                   'post' - print structure of tree postorder """
    print("\theight: "+str(bst_height(AVLTree))+", number of nods "+str(bst_count(AVLTree)))
    if type_of_moving == 'pre':
        print(return_avl_tree_preorder(AVLTree))
    elif type_of_moving == 'in':
        print(return_avl_tree_inorder(AVLTree))
    elif type_of_moving == 'post':
        print(return_avl_tree_postorder(AVLTree))






list_of_elements = [57, 16, 49, 19, 56, 12, 50, 26, 47, 51, 36, 1, 15, 46, 37, 11, 17, 35, 38, 42, 7, 33, 13, 44, 31, 8, 28, 3, 53, 39, 14, 52, 18, 45, 30, 34, 25]
#, 27, 2, 21, 32, 24, 29, 43, 54, 4, 59, 55, 41, 48, 9, 20, 23, 5, 58, 22, 40, 10] 
sorted_list_of_elements = list(list_of_elements)
sorted_list_of_elements.sort()

        
print("Tese of tree")
AVLTree = None
#AVLTree = AVLNode(key=5)
#print_status_of_tree(AVLTree)

for i in list_of_elements:
    AVLTree, _ = avl_node_insert(AVLTree, AVLNode(key=i))
    print_status_of_tree(AVLTree)



print("\n\nRemoving nodes\n\n")



delete_list = ['pl','pl','plp','plp','plp','plp','plp']
#delete_list = ['p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p','p']
for i in delete_list:
    print("delete "+i)
    tmp_node=AVLTree
    for j in range(0,len(i)):
        if i[j] == 'l':
            tmp_node = tmp_node.leftChild
        elif i[j] == 'p':
            tmp_node = tmp_node.rightChild
    AVLTree, _ = avl_node_delete(AVLTree, tmp_node)
    print_status_of_tree(AVLTree)



print(sorted_list_of_elements)

