{-# LANGUAGE TemplateHaskell #-}

module Offertex.Lib
  ( libF
  ) where

import           Control.Lens
import           Control.Monad.IO.Class
import           Control.Monad.Reader
import           Control.Monad.State.Lazy
import           Control.Monad.Writer.Lazy
import qualified Data.Map.Strict           as Map
import qualified Data.Text                 as Text
import           Text.Ginger.GVal
import           Text.Ginger.Parse
import           Text.Ginger.Run

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

data EnvBag = EnvBag {
  _symbolTable :: Map.Map Text.Text Text.Text
  } deriving Show
makeLenses 'EnvBag

context :: (Show p, MonadIO m, MonadWriter Text.Text m, MonadState EnvBag m) => GingerContext p m Text.Text
context = makeContextTextExM lookupVar tell warnAct

lookupVar :: (MonadIO m, MonadState EnvBag m) => Text.Text -> Run p m Text.Text (GVal (Run p m Text.Text))
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
      res <- runWriterT $ runStateT (runGingerT context template) (EnvBag Map.empty)
      liftIO $ print res
