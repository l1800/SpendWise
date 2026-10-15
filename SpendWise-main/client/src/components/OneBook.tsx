
import * as React from 'react';
import { styled } from '@mui/material/styles';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Collapse from '@mui/material/Collapse';
import IconButton, {type IconButtonProps } from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import type { Book } from '../models/Book';
import { UserContext } from '../context/userContext';
import { Link, useLocation } from 'react-router-dom';
import type { Lend } from '../models/Lend';
// import { addCommentById, getCommentById } from '../server/Book';
import { addLend } from '../server/lend';



interface ExpandMoreProps extends IconButtonProps {
  expand: boolean;
}
type BookProps={
  book:Book
}
const ExpandMore = styled((props: ExpandMoreProps) => {
  const { expand, ...other } = props;
  return <IconButton {...other} />;
})(({ theme }) => ({
  marginLeft: 'auto',
  transition: theme.transitions.create('transform', {
    duration: theme.transitions.duration.shortest,
  }),

}));

const  RecipeReviewCard:React.FC<BookProps>=({book})=> {
   const {user ,setUser} = React.useContext(UserContext);
    const [lends, setLends] = React.useState<Lend[]>([])
     const {state}=useLocation()

const toLendBookById = async (book:Book) => {
      
        try {
            const data={book:book,username:user?.userName,lendingdate:new Date()}
            const res=await addLend(data)
            setLends(res.data)
            
             
        }
        catch { 
            throw Error("error")     
        }
    }
 const [expanded, setExpanded] = React.useState(false);
  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <Card sx={{width:"250px"}}>
      <CardHeader sx={{backgroundImage:`url(${book.image})`,backgroundRepeat: "no-repeat",
      backgroundSize: "cover",
       height: "200px"}}/>
      <CardContent>
       <Typography variant="h6" sx={{ color: 'text.secondary' }}>
          {book.title}
        </Typography> 
      </CardContent>
      <CardActions disableSpacing>           
       {(
                        <button onClick={() => toLendBookById(book)}> להשאלת הספר</button>)}
        <ExpandMore
          expand={expanded}
           onClick={handleExpandClick}
          aria-expanded={expanded}
          aria-label="show more"
        >
          <ExpandMoreIcon />
        </ExpandMore>
      </CardActions>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <CardContent>
          <Typography>
          שם המחברת: {book.author}
          </Typography>
          <Typography>
            {book.pageCount}:מספר עמודים
          </Typography>
          <Typography>
           תקציר:{book.summery}
          </Typography>
          <Typography>
            
          </Typography>
          
        </CardContent>
      </Collapse>
    </Card>
    
  )
}
export default RecipeReviewCard