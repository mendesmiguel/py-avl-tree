"""
Copyright (c) 2018 Miguel Mendes, http://miguendes.me/

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from abc import ABCMeta, abstractmethod
from collections import deque
from copy import deepcopy
from typing import Iterable, Any, Union, TypeVar, Generator


class Comparable(metaclass=ABCMeta):
    @abstractmethod
    def __lt__(self, other: Any) -> bool: pass

    @abstractmethod
    def __gt__(self, other: Any) -> bool: pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool: pass


Entry = TypeVar('Entry', bound=Comparable)


class _EmptyAVLNode:
    """Internal object, represents an empty tree node using Null Object Pattern."""

    def __init__(self):
        self.height = 0

    def insert(self, entry: Entry):
        """Inserting a entry in a EmptyNode means returning a concrete node back."""
        return _AVLNode(entry)

    def delete(self, entry: Entry):
        """Cannot delete a entry from a EmptyNode"""
        raise KeyError(entry)

    @property
    def balance_factor(self):
        """The balance factor of a empty node is always 0."""
        return 0

    def pred(self, pred: Union['_AVLNode', '_EmptyAVLNode'], entry: Entry):
        raise KeyError(f'Predecessor of {entry} not found.')

    def succ(self, pred, entry):
        raise KeyError(f'Successor of {entry} not found.')

    def __bool__(self):
        """Empty node is always Falsy. """
        return False

    def __len__(self):
        """The lenght of a empty node is always 0."""
        return 0

    def __eq__(self, other):
        """Checks if a EmptyNode is equal to other"""
        return isinstance(other, self.__class__)


EMPTY_NODE = _EmptyAVLNode()


class _AVLNode:
    """Internal object, represents a tree node."""

    def __init__(self, entry: Entry = None):
        """Creates a new node."""
        self.entry: Entry = entry
        self.left: '_AVLNode' = EMPTY_NODE
        self.right: '_AVLNode' = EMPTY_NODE
        self.height: int = 1

    def insert(self, entry: Entry):
        """Inserts a entry to the subtree."""
        if entry > self.entry:
            self.right = self.right.insert(entry)
        elif entry < self.entry:
            self.left = self.left.insert(entry)

        return self._balanced_tree()

    def delete(self, entry: Entry) -> Union['_AVLNode', _EmptyAVLNode]:
        """Deletes a entry from subtree and return it balanced."""
        if entry > self.entry:
            self.right = self.right.delete(entry)
        elif entry < self.entry:
            self.left = self.left.delete(entry)
        else:
            if self.is_leaf():
                return EMPTY_NODE

            if self.left:
                new_entry = self.left.max()
                self.entry = new_entry
                self.left = self.left.delete(new_entry)
            else:
                return self.right

        return self._balanced_tree()

    def clear(self) -> _EmptyAVLNode:
        """Clears the whole subtree"""
        if self.is_leaf():
            return EMPTY_NODE
        self.left = self.left.clear()
        self.right = self.right.clear()

        return EMPTY_NODE

    def is_leaf(self) -> bool:
        """Checks if the node is a leaf node, i. e, if its siblings are empty."""
        return not (bool(self.left) or bool(self.right))

    def max(self) -> Entry:
        """Returns the max element in the subtree."""
        max_entry = self.entry
        right_node = self.right
        while right_node:
            max_entry = right_node.entry
            right_node = right_node.right

        return max_entry

    def min(self) -> Entry:
        """Returns the min element in the subtree."""
        min_entry = self.entry
        left_node = self.left
        while left_node:
            min_entry = left_node.entry
            left_node = left_node.left

        return min_entry

    @property
    def balance_factor(self) -> int:
        """Returns the balance factor of the node."""
        return self.left.height - self.right.height

    def __bool__(self) -> bool:
        """Returns True if the node is not None"""
        return self.entry is not None

    def __len__(self) -> int:
        """Return the number of elements in this subtree."""
        return 1 + len(self.left) + len(self.right)

    def __eq__(self, other) -> bool:
        """Checks if two nodes are equal."""
        return self.entry == other.entry and self.left == other.left and self.right == other.right

    def _balanced_tree(self) -> '_AVLNode':
        """Returns balanced tree after balance operation."""
        self._update_height()
        return self._balance_tree_if_unbalanced()

    def _update_height(self) -> None:
        """Updated the height if tree has been rebalanced."""
        self.height = 1 + max(self.left.height, self.right.height)

    def _balance_tree_if_unbalanced(self) -> '_AVLNode':
        """Performs the appropriate rotation if the the subtree is unbalanced."""
        if self.balance_factor == 2 and self.left.balance_factor == -1:
            return self._rotate_left_right()
        elif self.balance_factor == -2 and self.right.balance_factor == 1:
            return self._rotate_right_left()
        elif self.balance_factor == -2:
            return self._rotate_left()
        elif self.balance_factor == 2:
            return self._rotate_right()
        else:
            return self

    def _rotate_left(self) -> '_AVLNode':
        """Performs a left rotation."""
        right_tree = self.right
        self.right = right_tree.left
        right_tree.left = self

        self._update_height()
        right_tree._update_height()

        return right_tree

    def _rotate_right(self) -> '_AVLNode':
        """Performs a right rotation."""
        left_tree = self.left
        self.left = left_tree.right
        left_tree.right = self

        self._update_height()
        left_tree._update_height()

        return left_tree

    def _rotate_left_right(self) -> '_AVLNode':
        """Performs a LR rotation"""
        self.left = self.left._rotate_left()
        return self._rotate_right()

    def _rotate_right_left(self) -> '_AVLNode':
        """Performs a RL rotation"""
        self.right = self.right._rotate_right()
        return self._rotate_left()

    def pred(self, pred: Union['_AVLNode', _EmptyAVLNode], entry) -> Entry:
        if entry > self.entry:
            return self.right.pred(self, entry)
        elif entry < self.entry:
            return self.left.pred(pred, entry)
        else:
            if self.left:
                return self.left.max()
            if pred:
                return pred.entry

            raise KeyError(f'Predecessor of {entry} not found.')

    def succ(self, succ: Union['_AVLNode', _EmptyAVLNode], entry) -> Entry:
        if entry > self.entry:
            return self.right.succ(succ, entry)
        elif entry < self.entry:
            return self.left.succ(self, entry)
        else:
            if self.right:
                return self.right.min()
            if succ:
                return succ.entry

            raise KeyError(f'Successor of {entry} not found.')


class AVLTree:
    """
    AVLTree implements a balanced binary tree.

    Reference: http://en.wikipedia.org/wiki/AVL_tree

    In computer science, an AVL tree is a self-balancing binary search tree, and
    it is the first such data structure to be invented. In an AVL tree, the
    heights of the two child subtrees of any node differ by at most one;
    therefore, it is also said to be height-balanced. Lookup, insertion, and
    deletion all take O(log n) time in both the average and worst cases, where n
    is the number of nodes in the tree prior to the operation. Insertions and
    deletions may require the tree to be rebalanced by one or more tree rotations.
    The AVL tree is named after its two inventors, G.M. Adelson-Velskii and E.M.
    Landis, who published it in their 1962 paper "An algorithm for the
    organization of information."

    AVLTree expected comparable objects as entries.

    AVLTree() -> new empty tree.
    AVLTree(tree) -> new tree initialized from a tree
    AVLTree(seq) -> new tree initialized from seq [(entry1), (entry2), ... (entryN)]

    """

    def __init__(self, args: Iterable[Any] = None):
        """Initialize an AVL Tree. """
        self.root: _AVLNode = None
        self._init_tree(args)

    def insert(self, entry: Entry) -> None:
        """T.insert(entry) -- insert elem"""
        self.root = self.root.insert(entry)

    def delete(self, entry: Entry) -> None:
        """T.remove(entry) remove item <entry> from tree."""
        self.root = self.root.delete(entry)

    def traverse(self, order='inorder') -> Generator[Entry, None, None]:
        """Traverse the tree based on a given strategy.

        order : 'preorder' | 'postorder' | 'bfs' | default 'inorder'
            The traversal of the tree.

            Use 'preorder' to print the root first, then left and right subtree, respectively.
            Use 'postorder' to print the left and right subree first, then the root.
            Use 'bfs' to visit the tree in a breadth-first manner.
            The default is 'inorder' which prints the left subtree, the root and the right subtree.

        """
        if order == 'preorder':
            return self._preorder(self.root)
        elif order == 'postorder':
            return self._postorder(self.root)
        elif order == 'bfs':
            return self._bfs()
        else:
            return self._inorder(self.root)

    @property
    def height(self) -> int:
        """Returns the height of the tree. When the tree is empty its height is zero."""
        return self.root.height

    def search(self, entry: Entry) -> Entry:
        """Returns k if T has a entry k, else raise KeyError"""
        return self._search(entry).entry

    def _search(self, entry: Entry) -> _AVLNode:
        """Returns node.k if T has a entry k, else raise KeyError"""
        root = self.root

        while root:
            if entry > root.entry:
                root = root.right
            elif entry < root.entry:
                root = root.left
            else:
                return root

        raise KeyError(f'Entry {entry} not found.')

    def pred(self, entry: Entry) -> Entry:
        return self.root.pred(EMPTY_NODE, entry)

    def succ(self, entry: Entry) -> Entry:
        return self.root.succ(EMPTY_NODE, entry)

    def __len__(self) -> int:
        """T.__len__() <==> len(x). Retuns the number of elements in the tree."""
        return len(self.root)

    def __contains__(self, entry) -> bool:
        """k in T -> True if T has a entry k, else False"""
        try:
            self.search(entry)
            return True
        except KeyError:
            return False

    def max(self) -> Entry:
        """T.max() -> get the maximum entry of T."""
        return self.root.max()

    def min(self) -> Entry:
        """T.min() -> get the minimum entry of T."""
        return self.root.min()

    def clear(self) -> None:
        """T.clear() -> Removes all entries of T leaving it empty."""
        self.root = self.root.clear()

    def __repr__(self) -> str:
        """T.__repr__(...) <==> repr(x).
        Returns representation of the object that can be used to recreate the tree with the same values."""
        return f'{self.__class__.__name__}({list(self._bfs())})'

    def __str__(self) -> str:
        """T.__str__(...) <==> str(x)."""
        return repr(self)

    def __eq__(self, other) -> bool:
        """Checks if two trees are equal. """
        if isinstance(other, self.__class__):
            if self.height == other.height and len(self) == len(other):
                return self.root == other.root
        return False

    def __bool__(self) -> bool:
        """Returns True if the tree is not empty"""
        return bool(self.root)

    def __copy__(self) -> 'AVLTree':
        """Returns a shallow copy of the tree."""
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo) -> 'AVLTree':
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def _init_tree(self, args) -> None:
        """Initialize the tree according to the arguments passed. """
        self.root = EMPTY_NODE

        if args is not None:
            if isinstance(args, self.__class__):
                args = args.traverse('bfs')

            try:
                for entry in args:
                    self.insert(entry)
            except (ValueError, TypeError) as e:
                raise TypeError('AVLTree constructor called with '
                                f'incompatible data type: {e}')

    def _inorder(self, root) -> Generator[Entry, None, None]:
        """Performs an in-order traversal. """
        if root:
            yield from self._inorder(root.left)
            yield root.entry
            yield from self._inorder(root.right)

    def _preorder(self, root) -> Generator[Entry, None, None]:
        """Performs an pre-order traversal."""
        if root:
            yield root.entry
            yield from self._preorder(root.left)
            yield from self._preorder(root.right)

    def _postorder(self, root) -> Generator[Entry, None, None]:
        """Performs an post-order traversal."""
        if root:
            yield from self._postorder(root.left)
            yield from self._postorder(root.right)
            yield root.entry

    def _bfs(self) -> Generator[Entry, None, None]:
        """Performs an Breadth first traversal."""
        root = self.root

        if root:
            q = deque()
            q.append(root)

            while q:
                root = q.popleft()
                if not root:
                    continue

                yield root.entry
                left = root.left
                right = root.right

                q.append(left)
                q.append(right)
