from Crypto.Cipher import DES
import argparse

class PinBlock:
    def __init__(self, pin, pan, twk, tmk):
        self.pin = pin
        self.pan = pan
        self.twk = twk
        self.tmk = tmk
    
    def clear_pin_block(self):
        """This function computes pin block given that we have acquired the working key.
        It computes as following:
            p1 = [0] + [pin_length] + [pin] + [10*f]
            p2 = [0000] + last_12_digits_of_pan_length-1
            clear PIN Block = p1 XOR p2
        """
        p1 = "0" + str(len(self.pin)) + str(self.pin) + 10 * "f"
        p2 = 4 * "0" + self.pan[:-1][-12:]
        assert len(p2) == len(p1)
        clear_pin_block = hex(int(p1, 16) ^ int(p2, 16))
        print(f"The clear (XOR) pin block is: {clear_pin_block}") 
        return "0" + clear_pin_block[2:]


    def decrypt_workingkey(self):
        """
        p1 = [0] + [pin_length] + [pin] + [10*f]
        p2 = [0000] + last_12_digits_of_pan_length-1
        clear PIN Block = p1 XOR p2
        Use the decrypted working key as the key for DES
        Use DES to encrypt the clear PIN Block
        """
        des_master_key = DES.new(bytes.fromhex(self.tmk))
        decrypted_working_key = des_master_key.decrypt(bytes.fromhex(self.twk))
        print(f"The encrypted working key is: {decrypted_working_key.hex()}")

        return decrypted_working_key.hex()

    def get_clear_pin_block(self, pinblock):
        key = DES.new(bytes.fromhex(self.decrypt_workingkey()))
        pin_block = key.decrypt(bytes.fromhex(pinblock))
        return pin_block.hex()

    def xor_pinblock(self, pinblock):
        
        p2 = 4 * "0" + self.pan[:-1][-12:]
        assert len(p2) == len(pinblock)
        clear_pin_block = hex(int(pinblock, 16) ^ int(p2, 16))
        print(f"The clear (XOR) pin block is: {clear_pin_block}") 
        return "0" + clear_pin_block[2:]

    def reverse_pin(self, pinblock):
        clear_pin = self.get_clear_pin_block(pinblock)
        xor_pin = self.xor_pinblock(clear_pin)
        return self.get_pin(xor_pin)

    def get_pin(self, xor):
        # p1 = "0" + str(len(self.pin)) + str(self.pin) + 10 * "f"
        return xor[2:2+4]

    def encrypted_pin_block(self):
        """This function computes the pin block.
        1. decrypt the working key using the masterkey
        2. encrypt the clear pin block using the decrypted working key
        3. return the encrypted pin block
        """
        clear_pin_block = self.clear_pin_block()
        des_master_key = DES.new(bytes.fromhex(self.tmk))
        decrypted_working_key = des_master_key.decrypt(bytes.fromhex(self.twk))
        print(f"The decrypted working key is: f{decrypted_working_key.hex(), len(decrypted_working_key)}")
        assert isinstance(decrypted_working_key, bytes)
        d = DES.new(decrypted_working_key)
        pin_block = d.encrypt(bytes.fromhex(clear_pin_block))
        return pin_block.hex()


if __name__ == "__main__":
    #pan = "6392560017624665"
    #pin = "2506"
    #pan = "9222081700176714465"
    #pin = "0000"
    #twk = "a9eb3c0c929ddcae"


    parser = argparse.ArgumentParser()
    parser.add_argument("-pan")
    parser.add_argument("-pin")
    parser.add_argument("-tmk", default="E6FBFD2C914A155D")
    parser.add_argument("-twk")
    args = parser.parse_args()
    pin = args.pin
    pan = args.pan
    twk = args.twk
    tmk = args.tmk
    print(pin, pan, twk, tmk)
    api = PinBlock(pin, pan, twk, tmk)
    print(api.encrypted_pin_block())
    print(api.decrypt_workingkey())
    pinblock = api.reverse_pin("d122f06d07b3ef95")
    print(f"The reverse pin is: {pinblock}")
    
