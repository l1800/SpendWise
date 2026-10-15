import type { Book } from "./Book";
import type { User } from "./Users";

export type Lend={
  user:User
    lendingDate:Date;
    book:Book
}  
