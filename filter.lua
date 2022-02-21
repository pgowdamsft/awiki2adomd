local text = pandoc.text

function Span(el)
    if el.identifier == "title-text" then
      return el.content
    end
    if el.classes[1] == "confluence-embedded-file-wrapper" then
      return el.content
    end
    return el

end

function Div(el)
  if el.identifier == "footer" then
    return {}
  end
  if el.identifier == "page" 
    or el.identifier == "main" 
    or el.identifier == "main-header"
    or el.identifier == "main-content"
    or el.identifier == "content" 
    or el.classes[1] == "pageSection" 
    or el.classes[1] == "pageSectionHeader"
    or el.classes[1] == "code"
    or el.classes[1] == "codeContent"
    or el.identifier == "breadcrumb-section" 
     then
      return el.content
  end
  if el.classes[1] == "page-metadata"  then
    return {}
  end
end

function Image(el)
  if el.classes[1] == "confluence-embedded-image" then
    return {
        pandoc.Image({pandoc.Str(el.title)}, el.src),
        pandoc.Str("\n"),
        pandoc.cr
      }
  end
  return el
end

