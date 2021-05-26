#!/usr/bin/env python
'''
The cache is essentially a dictionary which, in addition to mapping keys to values, tracks
relative positions of keys. The prototypical structure is:
{
  <key1>: {
    "value": <value1>,
    "next": None,
    "prev": <key3>
  },
  <key2>: {
    "value": <value2>,
    "next": <key3>,
    "prev": None
  },
  <key3>: {
    "value": <value3>,
    "next": <key1>,
    "prev": <key2>
  }
}
Note above that although the order of the keys is implied by their prev and next fields, the order
that the keys appear in the dictionary may be unrelated.

The lru and most recently used keys are tracked separately.
'''
class LRUCache:
    def __init__(self, max_size):
        self._max_size = max_size
        if max_size < 1:
            raise ValueError("Size must be greater than 0")
        self._current_size = 0

        self._lru_key = None
        self._mru_key = None

        # maps keys to values. it also indicates the keys which come
        # before it and after it in the lru queue, which it simulates
        # in this manner
        self._cache = {}

    @property
    def max_size(self):
        return self._max_size

    # updates the keys surrounding the current one. returns False if no such update is necessary
    def _update_existing_key_position_context(self, key):
        position_info = self._cache[key]
        prev_key = position_info['prev']
        next_key = position_info['next']
        if next_key == None:
            # everything is already in the right place. return false to indicate that no contextual
            # update was done
            return False
        elif prev_key == None:
            # the key was the least recently used key. we must update the lru_key to be
            # the next least recently used key
            self._lru_key = next_key
            self._cache[next_key]['prev'] = None
        else:
            # the updated key falls in the middle of the list. its neighbors must be joined together
            self._cache[prev_key]['next'] = next_key
            self._cache[next_key]['prev'] = prev_key
        return True

    def put(self, key, value):
        if key in self._cache:
            if not self._update_existing_key_position_context(key):
                # if the above function returns false, we need only update the value
                # associated with the key. the context has not changed
                self._cache[key]["value"] = value
                return
        else:
            # here we are adding a new key to the list. we must check whether this addition
            # will require us to delete the lru key
            if self._current_size == self.max_size:
                upcoming_lru_key = self._cache[self._lru_key]['next']
                # handle the case where the max size is 1
                if upcoming_lru_key is None:
                    del self._cache[self._lru_key]
                    self._lru_key = key
                    self._cache[key] = {
                        "value": value,
                        "prev": None,
                        "next": None
                    }
                    self._mru_key = key
                    return
                else:
                    self._cache[upcoming_lru_key]['prev'] = None
                    del self._cache[self._lru_key]
                    self._lru_key = upcoming_lru_key
            else:
                self._current_size += 1
        if self._mru_key is not None:
            self._cache[self._mru_key]['next'] = key

        if self._lru_key is None:
            self._lru_key = key

        self._cache[key] = {
            "value": value,
            "prev": self._mru_key,
            "next": None
        }
        self._mru_key = key

    def get(self, key):
        if key in self._cache:
            value = self._cache[key]['value']
            # this key needs to be made the most recently used key
            self._update_existing_key_position_context(key)
            if self._mru_key is not None:
                self._cache[self._mru_key]['next'] = key
                self._cache[key]['prev'] = self._mru_key
                self._cache[key]['next'] = None
            self._mru_key = key
            return value
        else:
            return None

    def delete(self, key):
        if key in self._cache:
            # updating the context of the deleted key. 
            # we need to handle the case in which we are deleting the final key
            if not self._update_existing_key_position_context(key):
                new_mru = self._cache[key]['prev']

                if new_mru is not None:
                    self._cache[new_mru]['next'] = None
                    self._mru_key = new_mru
                
            # handle the case where there is only one key and we are deleting it
            # note that in updating the current context, the key parameter will not
            # be the lru key unless it is the only key currently in the cache
            if key == self._lru_key:
                self._lru_key = None
            if key == self._mru_key:
                self._mru_key = None

            del self._cache[key]
            self._current_size -= 1
        else:
            return

    def reset(self):
        self._cache = {}
        self._current_size = 0
        self._mru_key = None
        self._lru_key = None