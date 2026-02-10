class SoftwareCipher:
    """
    Wrapper for software-based encryption.
    Keeps the same interface as the hardware cipher.
    """

    def __init__(self, controller):
        """
        cipher: instance of AES, DES, etc.
        """
        self.controller = controller
        self.config = controller.config
        self.dp = controller.data_processing 

    def block_lab_operation(self, single_block): 
        #must do the aes cipher, based on the key size, mode of operation and direction : enc/dec. 
        #all this info is in the dict self.config which comes from the controller object, which is the center of the program
        #here is the structure of the dict: 
        #self.config = {
        #    "mode": None,
        #    "key_size": None,
        #    "key": None,
        #    "iv": None, 
        #    "direction": "enc"
        #}
        #expected return : 
        #{
        #"rounds": ["001122...", "AABBCC...", ...],
        #"final": "FFEEDD..."
        #}
        
        pass

