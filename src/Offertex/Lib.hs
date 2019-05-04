module Offertex.Lib
  ( libF
  ) where

import           Control.Lens
import           Control.Monad.IO.Class
import           Control.Monad.Writer.Lazy
import qualified Data.Text                 as Text
import           Text.Ginger.GVal
import           Text.Ginger.Parse
import           Text.Ginger.Run
import           Text.Ginger.Run.Type

parseOpts :: MonadIO m => ParserOptions m
parseOpts = ParserOptions
        { poIncludeResolver = liftIO . fmap Just . readFile
        , poSourceName = Nothing
        , poKeepTrailingNewline = False
        , poLStripBlocks = False
        , poTrimBlocks = False
        , poDelimiters = Delimiters
          { delimOpenInterpolation = "<<"
          , delimCloseInterpolation = ">>"
          , delimOpenTag = "<?"
          , delimCloseTag = "?>"
          , delimOpenComment = "<!--"
          , delimCloseComment = "-->"
          }
        }

context :: (Show p, MonadIO m, MonadWriter Text.Text m) => GingerContext p m Text.Text
context = makeContextTextExM lookupVar tell warnAct

lookupVar :: (MonadIO m) => Text.Text -> Run p m Text.Text (GVal (Run p m Text.Text))
lookupVar varname = do
  liftIO $ print $ "get " <> varname
  pure $ toGVal $ "result " <> varname

warnAct :: (Show p, MonadIO m) => RuntimeError p -> m ()
warnAct = liftIO . print

libF :: MonadIO m => m ()
libF = do
  fileRes <- liftIO $ readFile "offer.tex"
  parsed <- parseGinger' parseOpts fileRes
  case parsed of
    Left err -> liftIO $ print err
    Right template -> do
      res <- runWriterT $ runGingerT context template
      liftIO $ print res
