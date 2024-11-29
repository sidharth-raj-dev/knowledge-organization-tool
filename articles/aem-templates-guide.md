# Understanding AEM Templates: A Comprehensive Guide

## Table of Contents
1. Types of Templates
2. Static Templates (Classic/Legacy)
3. Template Properties In-Depth
4. Component Inheritance
5. Template Hierarchies
6. Best Practices

## 1. Types of Templates

AEM offers two types of templates:

### 1.1 Static/Classic Templates
- Located in `/apps/<project>/templates/`
- Require developer intervention for changes
- Defined in single `.content.xml` files
- Less flexible but simpler structure

### 1.2 Editable Templates (Modern)
- Located in `/conf/<project>/settings/wcm/templates/`
- Can be modified by authors
- More complex structure with separate folders for structure/policies
- More flexible but requires more setup

## 2. Static Templates Deep Dive

Let's examine a static template in detail:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jcr:root xmlns:sling="http://sling.apache.org/jcr/sling/1.0" 
          xmlns:cq="http://www.day.com/jcr/cq/1.0" 
          xmlns:jcr="http://www.jcp.org/jcr/1.0"
          jcr:primaryType="cq:Template"
          jcr:title="News Article"
          jcr:description="Template for news articles"
          allowedPaths="[/content/mysite/news/*]"
          allowedParents="[/apps/mysite/templates/news-section]"
          allowedChildren="[/apps/mysite/templates/news-subsection]"
          ranking="{Long}100"
          resourceSuperType="mysite/components/page/basepage">

    <jcr:content
        jcr:primaryType="cq:PageContent"
        sling:resourceType="mysite/components/pages/newsarticle">
        
        <header
            jcr:primaryType="nt:unstructured"
            sling:resourceType="mysite/components/header"/>
            
        <content
            jcr:primaryType="nt:unstructured"
            sling:resourceType="wcm/foundation/components/parsys"/>
            
        <sidebar
            jcr:primaryType="nt:unstructured"
            sling:resourceType="mysite/components/sidebar"/>
            
        <footer
            jcr:primaryType="nt:unstructured"
            sling:resourceType="mysite/components/footer"/>
    </jcr:content>
</jcr:root>
```

## 3. Template Properties In-Depth

### 3.1 Basic Properties

```xml
jcr:title="News Article"              <!-- Display name in AEM UI -->
jcr:description="Template for news"    <!-- Description shown in template selector -->
ranking="{Long}100"                    <!-- Order in template picker -->
status="enabled"                       <!-- Template availability -->
```

### 3.2 Path Control Properties

#### allowedPaths
Controls where pages can be created using this template:

```xml
<!-- Single path -->
allowedPaths="/content/mysite/*"

<!-- Multiple paths -->
allowedPaths="[/content/mysite/news/*, /content/mysite/press/*]"

<!-- Real-world examples -->
<!-- Corporate website with multiple brands -->
<jcr:root
    jcr:primaryType="cq:Template"
    jcr:title="Brand Product Page"
    allowedPaths="[/content/brand1/products/*, /content/brand2/products/*]"
/>

<!-- Language-specific template -->
<jcr:root
    jcr:primaryType="cq:Template"
    jcr:title="UK Article"
    allowedPaths="/content/mysite/en-gb/*"
/>
```

#### allowedParents
Specifies which templates can be parent pages:

```xml
<!-- Basic example -->
allowedParents="[/apps/mysite/templates/section-landing]"

<!-- Multiple parent templates -->
allowedParents="[
    /apps/mysite/templates/category-page,
    /apps/mysite/templates/landing-page
]"

<!-- Real-world example: News site hierarchy -->
<!-- Section Template -->
<jcr:root
    jcr:primaryType="cq:Template"
    jcr:title="News Section"
    allowedParents="[/apps/newssite/templates/homepage]"
    allowedPaths="/content/newssite/*"
/>

<!-- Article Template -->
<jcr:root
    jcr:primaryType="cq:Template"
    jcr:title="News Article"
    allowedParents="[/apps/newssite/templates/news-section]"
    allowedPaths="/content/newssite/news/*"
/>
```

#### allowedChildren
Controls which templates can be used for child pages:

```xml
<!-- Basic example -->
allowedChildren="[/apps/mysite/templates/article]"

<!-- Multiple child templates -->
allowedChildren="[
    /apps/mysite/templates/product,
    /apps/mysite/templates/product-variant
]"
```

### 3.3 Component Inheritance with resourceSuperType

The `resourceSuperType` property enables component inheritance, allowing templates to build upon existing functionality:

```xml
<!-- Base Page Template -->
<jcr:root
    jcr:primaryType="cq:Template"
    jcr:title="Base Page"
    resourceSuperType="wcm/foundation/components/page">
    <jcr:content
        jcr:primaryType="cq:PageContent"
        sling:resourceType="mysite/components/page/basepage">
        <!-- Base structure -->
    </jcr:content>
</jcr:root>

<!-- Product Page Template inheriting from Base -->
<jcr:root
    jcr:primaryType="cq:Template"
    jcr:title="Product Page"
    resourceSuperType="mysite/components/page/basepage">
    <jcr:content
        jcr:primaryType="cq:PageContent"
        sling:resourceType="mysite/components/page/productpage">
        <!-- Additional product-specific structure -->
    </jcr:content>
</jcr:root>
```

Component Structure for Inheritance:

```
/apps/mysite/components/page/
    basepage/
        basepage.html        <!-- Base layout -->
        header.html
        footer.html
        customheaderlibs.html
        customfooterlibs.html
    
    productpage/
        productpage.html     <!-- Extends base layout -->
        product-details.html <!-- Additional components -->
        product-gallery.html
```

## 4. Real-World Template Hierarchy Example

Here's a complete example of a website template hierarchy:

```xml
<!-- Homepage Template -->
<jcr:root
    jcr:primaryType="cq:Template"
    jcr:title="Homepage"
    allowedPaths="/content/mysite"
    allowedChildren="[
        /apps/mysite/templates/section-landing,
        /apps/mysite/templates/category-landing
    ]"
    resourceSuperType="mysite/components/page/basepage">
</jcr:root>

<!-- Section Landing Template -->
<jcr:root
    jcr:primaryType="cq:Template"
    jcr:title="Section Landing"
    allowedPaths="/content/mysite/*"
    allowedParents="[/apps/mysite/templates/homepage]"
    allowedChildren="[
        /apps/mysite/templates/article,
        /apps/mysite/templates/gallery
    ]"
    resourceSuperType="mysite/components/page/basepage">
</jcr:root>

<!-- Article Template -->
<jcr:root
    jcr:primaryType="cq:Template"
    jcr:title="Article"
    allowedPaths="/content/mysite/*/articles"
    allowedParents="[/apps/mysite/templates/section-landing]"
    resourceSuperType="mysite/components/page/articlepage">
</jcr:root>
```

This creates a structure like:
```
Homepage (homepage template)
    └── News (section-landing template)
         └── Article 1 (article template)
         └── Article 2 (article template)
    └── Products (section-landing template)
         └── Product A (article template)
         └── Product B (article template)
```

## 5. Best Practices

1. Template Naming
```xml
<!-- Good -->
jcr:title="Product Detail Page"
<!-- Bad -->
jcr:title="Template_Product_Detail_01"
```

2. Path Restrictions
```xml
<!-- Good - Specific paths -->
allowedPaths="[/content/mysite/products/*]"
<!-- Bad - Too broad -->
allowedPaths="/content/*"
```

3. Inheritance
```xml
<!-- Good - Clear inheritance chain -->
resourceSuperType="mysite/components/page/basepage"
<!-- Bad - Skipping inheritance levels -->
resourceSuperType="wcm/foundation/components/page"
```

4. Template Hierarchy
```xml
<!-- Good - Clear parent/child relationships -->
allowedParents="[/apps/mysite/templates/product-category]"
allowedChildren="[/apps/mysite/templates/product-variant]"
<!-- Bad - No restrictions -->
allowedParents="[/*]"
```

Remember:
- Keep template hierarchy logical and simple
- Use clear, descriptive names
- Restrict template usage to appropriate paths
- Leverage inheritance to avoid code duplication
- Document template purpose and usage
